from mcp.server.fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    @mcp.prompt(name="analisar_ciclo")
    def analisar_ciclo(id_ciclo: int) -> str:
        """Orienta uma análise segura de ciclo."""
        return (
            f"Analise o ciclo {id_ciclo}. Comece por ciclo_visao_geral, consulte "
            "ciclo_riscos_pendencias e use tools específicas apenas quando necessário. "
            "Não invente dados ausentes e preserve o escopo da empresa autenticada."
        )

    @mcp.prompt(name="gerar_relatorio_ciclo")
    def gerar_relatorio_ciclo(id_ciclo: int) -> str:
        """Orienta a geração de um relatório estruturado."""
        return (
            f"Use ciclo_relatorio_completo para o ciclo {id_ciclo} e produza um relatório "
            "com resumo executivo, evidências, riscos, responsáveis e próximos passos. "
            "Diferencie fatos retornados pelas tools de recomendações."
        )
