from datetime import datetime
from typing import Any

from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.core.context import get_request_context
from acta_mcp.core.tooling import execute_tool


def register_memory_tools(mcp: FastMCP, container: Container) -> None:
    service = container.memoria
    audit = container.audit

    def execute(name: str, operation):
        return execute_tool(name=name, audit=audit, operation=operation)

    @mcp.tool(name="memoria_garantir_sessao", structured_output=True)
    def garantir_sessao(session_id: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        """Cria ou valida uma sessão pertencente ao usuário e empresa autenticados."""
        context = get_request_context()
        return execute(
            "memoria_garantir_sessao",
            lambda: service.garantir_sessao(context, session_id=session_id, metadata=metadata),
        )

    @mcp.tool(name="memoria_salvar_mensagem", structured_output=True)
    def salvar_mensagem(
        session_id: str,
        role: str,
        content: str,
        agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Persiste uma mensagem sanitizada na sessão autenticada."""
        context = get_request_context()
        return execute(
            "memoria_salvar_mensagem",
            lambda: service.salvar_mensagem(
                context,
                session_id=session_id,
                role=role,
                content=content,
                agent=agent,
                metadata=metadata or {},
            ),
        )

    @mcp.tool(name="memoria_obter_contexto", structured_output=True)
    def obter_contexto(
        session_id: str, pergunta: str | None = None, limit: int | None = None
    ) -> dict[str, Any]:
        """Combina resumo, mensagens recentes, preferências e memórias semanticamente relevantes."""
        context = get_request_context()
        return execute(
            "memoria_obter_contexto",
            lambda: service.obter_contexto(
                context, session_id=session_id, pergunta=pergunta, limit=limit
            ),
        )

    @mcp.tool(name="memoria_material_resumo", structured_output=True)
    def material_resumo(session_id: str) -> dict[str, Any]:
        """Retorna apenas mensagens ainda não consolidadas e indica quando resumir."""
        context = get_request_context()
        return execute(
            "memoria_material_resumo",
            lambda: service.material_resumo(context, session_id=session_id),
        )

    @mcp.tool(name="memoria_atualizar_resumo", structured_output=True)
    def atualizar_resumo(session_id: str, resumo: str, resumido_ate: datetime) -> dict[str, Any]:
        """Salva um resumo produzido pelo acta-ai e avança o marcador incremental."""
        context = get_request_context()
        return execute(
            "memoria_atualizar_resumo",
            lambda: service.atualizar_resumo(
                context, session_id=session_id, resumo=resumo, resumido_ate=resumido_ate
            ),
        )

    @mcp.tool(name="memoria_registrar", structured_output=True)
    def registrar(
        tipo: str,
        conteudo: str,
        origem: str = "explicita",
        confianca: float = 1.0,
        session_id_origem: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Registra preferência, decisão, objetivo ou ponto relevante conforme consentimento."""
        context = get_request_context()
        return execute(
            "memoria_registrar",
            lambda: service.registrar(
                context,
                tipo=tipo,
                conteudo=conteudo,
                origem=origem,
                confianca=confianca,
                session_id_origem=session_id_origem,
                metadata=metadata or {},
            ),
        )

    @mcp.tool(name="memoria_buscar", structured_output=True)
    def buscar(pergunta: str, limit: int = 6) -> dict[str, Any]:
        """Busca semanticamente memórias do usuário dentro da empresa autenticada."""
        context = get_request_context()
        return execute(
            "memoria_buscar", lambda: service.buscar(context, pergunta=pergunta, limit=limit)
        )

    @mcp.tool(name="memoria_listar", structured_output=True)
    def listar(tipo: str | None = None, limit: int = 50) -> dict[str, Any]:
        """Lista memórias ativas para transparência e controle do usuário."""
        context = get_request_context()
        return execute("memoria_listar", lambda: service.listar(context, tipo=tipo, limit=limit))

    @mcp.tool(name="memoria_excluir", structured_output=True)
    def excluir(id_memoria: str) -> dict[str, Any]:
        """Exclui uma memória do usuário conforme a política de retenção."""
        context = get_request_context()
        return execute("memoria_excluir", lambda: service.excluir(context, id_memoria=id_memoria))

    @mcp.tool(name="memoria_obter_consentimento", structured_output=True)
    def obter_consentimento() -> dict[str, Any]:
        """Consulta a política de memória escolhida pelo usuário nesta empresa."""
        context = get_request_context()
        return execute("memoria_obter_consentimento", lambda: service.obter_consentimento(context))

    @mcp.tool(name="memoria_configurar_consentimento", structured_output=True)
    def configurar_consentimento(modo: str, retencao_dias: int | None = None) -> dict[str, Any]:
        """Ativa, limita ou desativa a memória longa; desativar apaga memórias ativas."""
        context = get_request_context()
        return execute(
            "memoria_configurar_consentimento",
            lambda: service.configurar_consentimento(
                context, modo=modo, retencao_dias=retencao_dias
            ),
        )
