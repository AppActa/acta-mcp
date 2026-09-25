import json
import re
import unicodedata
from datetime import UTC, datetime
from io import BytesIO
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from pymongo import ReturnDocument
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from acta_mcp.core.context import RequestContext
from acta_mcp.core.exceptions import NotFoundError
from acta_mcp.infrastructure.serializers import serialize
from acta_mcp.modules.common import AccessService
from acta_mcp.modules.licoes.schemas import LessonDraft


class LicoesService:
    def __init__(self, mongo, repository, access: AccessService, settings) -> None:
        self.mongo, self.repository = mongo, repository
        self.access, self.settings = access, settings

    def _lessons(self):
        return self.mongo.database["licoes_aprendidas"]

    def _model(self):
        if not self.settings.gemini_api_key:
            raise RuntimeError("Modelo de lições aprendidas não configurado.")
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=self.settings.gemini_api_key, temperature=0)

    def _overview(self, context: RequestContext, id_ciclo: int) -> dict:
        reports = list(self.mongo.database["relatorios"].find({"id_empresa": context.empresa_id, "id_ciclo": id_ciclo}, {"_id": 0}).sort("criado_em", -1))
        if len(reports) >= 5:
            return {"fonte": "relatorios", "relatorios": reports}
        row = self.repository.overview(empresa_id=context.empresa_id, id_ciclo=id_ciclo)
        if row is None:
            raise NotFoundError("Ciclo não encontrado para a empresa autenticada.")
        return {"fonte": "relatorios_e_cte", "relatorios": reports, "overview_sql": row}

    def criar(self, context: RequestContext, *, id_ciclo: int, contexto: str, expectativa: str) -> dict:
        self.access.ensure_cycle(context, id_ciclo)
        overview = self._overview(context, id_ciclo)
        prompt = ("Crie uma lição aprendida somente com as evidências JSON fornecidas. "
                  "Não invente fatos. Retorne JSON com titulo, licao, categoria, tags (máximo 5).\n"
                  f"Expectativa: {expectativa}\nContexto: {contexto}\nEvidências: {json.dumps(overview, ensure_ascii=False, default=str)}")
        raw = self._model().invoke(prompt).content
        if isinstance(raw, list):
            raw = "".join(str(p.get("text", "")) if isinstance(p, dict) else str(p) for p in raw)
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", str(raw).strip(), flags=re.I)
        draft = LessonDraft.model_validate_json(cleaned[cleaned.find("{"):cleaned.rfind("}")+1])
        now = datetime.now(UTC)
        counter = self.mongo.database["counters"].find_one_and_update({"_id": "licoes_aprendidas"}, {"$inc": {"seq": 1}}, upsert=True, return_document=ReturnDocument.AFTER)
        lesson = {"id_licao": int(counter["seq"]), "id_empresa": context.empresa_id, "id_ciclo": id_ciclo,
                  "contexto": contexto, "expectativa": expectativa, **draft.model_dump(),
                  "fonte": "acta-mcp", "criado_em": now}
        self._lessons().insert_one(lesson)
        asset = None
        try:
            from cloudinary import config as cloudinary_config
            from cloudinary import uploader
            cloudinary_config(cloud_name=self.settings.cloudinary_cloud_name, api_key=self.settings.cloudinary_api_key,
                              api_secret=self.settings.cloudinary_api_secret, secure=True)
            buffer = BytesIO()
            styles = getSampleStyleSheet()
            doc = SimpleDocTemplate(buffer, pagesize=A4, title=draft.titulo)
            doc.build([Paragraph("Lição Aprendida", styles["Title"]), Spacer(1, 12),
                       Paragraph(draft.titulo, styles["Heading1"]), Paragraph(draft.licao, styles["BodyText"]),
                       Paragraph(f"Categoria: {draft.categoria}", styles["BodyText"]),
                       Paragraph(f"Fonte do overview: {overview['fonte']}", styles["BodyText"])])
            company_name = self.repository.company_name(empresa_id=context.empresa_id)
            if company_name is None:
                raise NotFoundError("Empresa não encontrada.")
            folder = unicodedata.normalize("NFKD", company_name).encode("ascii", "ignore").decode().lower()
            folder = re.sub(r"[^a-z0-9]+", "-", folder).strip("-") or f"empresa-{context.empresa_id}"
            uploaded = uploader.upload(buffer.getvalue(), resource_type="raw", folder=folder, public_id=f"licao-{lesson['id_licao']}")
            asset = uploaded["public_id"]
            attachment = self.repository.create_attachment(
                usuario_id=context.usuario_id, empresa_id=context.empresa_id, id_ciclo=id_ciclo,
                id_licao=lesson["id_licao"], filename=f"licao-{lesson['id_licao']}.pdf",
                size=len(buffer.getvalue()), bucket=folder, url=uploaded["secure_url"],
            )
            lesson.pop("_id", None)
            return {"status":"ok", "licao":serialize(lesson), "anexo":attachment}
        except Exception:
            self._lessons().delete_one({"id_licao": lesson["id_licao"], "id_empresa": context.empresa_id})
            if asset:
                from cloudinary import uploader
                uploader.destroy(asset, resource_type="raw")
            raise

    def _find(self, context: RequestContext, id_ciclo: int | None) -> list[dict]:
        if id_ciclo is not None:
            self.access.ensure_cycle(context, id_ciclo)
        query: dict[str, Any] = {"id_empresa": context.empresa_id}
        if id_ciclo is not None:
            query["id_ciclo"] = id_ciclo
        return list(self._lessons().find(query, {"_id": 0}).sort("criado_em", -1))

    def resumir(self, context: RequestContext, id_ciclo: int | None = None) -> dict:
        lessons = self._find(context, id_ciclo)
        if not lessons:
            return {"status": "sem_licoes"}
        response = self._model().invoke("Resuma em português, sem inventar e usando apenas estas lições: " + json.dumps(lessons, ensure_ascii=False, default=str))
        return {"status":"ok", "resumo":str(response.content).strip()}

    def perguntar(self, context: RequestContext, *, id_ciclo: int, pergunta: str) -> dict:
        lessons = self._find(context, id_ciclo)
        if not lessons:
            return {"status":"sem_evidencia"}
        response = self._model().invoke("Responda em português usando somente as lições JSON. Se não houver evidência suficiente, responda que não há evidência suficiente.\nPergunta: " + pergunta + "\nLições: " + json.dumps(lessons, ensure_ascii=False, default=str))
        answer = str(response.content).strip()
        return {"status":"ok", "resposta":answer, "referencias":[item["id_licao"] for item in lessons]}
