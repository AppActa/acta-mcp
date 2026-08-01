SCHEMA_SUMMARY = """
PostgreSQL:
- empresa, usuario_sistema, colaborador
- pdca.ciclo, pdca.meta, pdca.problema, pdca.causa_raiz
- pdca.plano_acao, pdca.tarefa, pdca.tarefa_dependencia
- pdca.alerta_prazo, pdca.treinamento, pdca.usuario_treinamento
- pdca.usuario_ciclo, pdca.verificacao_resultado

MongoDB (sempre filtrado por id_ciclo e id_empresa):
- ishikawa
- perdas_ganhos
- justificativas_tarefas
- competencias_colaborador
- disponibilidade_colaborador
- realocacoes_colaborador

Não existe tool de SQL ou MongoDB livre.
""".strip()

