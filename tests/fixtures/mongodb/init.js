const acta = db.getSiblingDB("acta");

acta.ishikawa.insertMany([
  {
    id_ciclo: 1,
    id_empresa: 1,
    problema: "Retrabalho alto",
    causas: { metodo: ["Ausência de padrão"], mao_de_obra: ["Treinamento incompleto"] }
  },
  {
    id_ciclo: 2,
    id_empresa: 2,
    problema: "Dado confidencial",
    causas: { metodo: ["Não deve vazar"] }
  }
]);

acta.justificativas_tarefas.insertOne({
  id_ciclo: 1,
  id_empresa: 1,
  id_tarefa: 1,
  justificativa: "Dependência de validação da operação."
});

acta.competencias_colaborador.insertMany([
  {
    id_ciclo: 1,
    id_empresa: 1,
    id_colaborador: 2,
    id_usuario: 2,
    competencias: ["Análise de processos", "Dados"]
  },
  {
    id_ciclo: 1,
    id_empresa: 1,
    id_colaborador: 3,
    id_usuario: 3,
    competencias: ["Operações", "Treinamento"]
  }
]);

acta.disponibilidade_colaborador.insertMany([
  {
    id_ciclo: 1,
    id_empresa: 1,
    id_colaborador: 2,
    id_usuario: 2,
    horas_semanais_disponiveis: 8
  },
  {
    id_ciclo: 1,
    id_empresa: 1,
    id_colaborador: 3,
    id_usuario: 3,
    horas_semanais_disponiveis: 12
  }
]);

acta.realocacoes_colaborador.insertOne({
  id_ciclo: 1,
  id_empresa: 1,
  id_colaborador: 3,
  id_usuario: 3,
  motivo: "Apoio temporário à validação"
});

acta.formularios.insertMany([
  {
    id_resposta: "resposta-fenomeno-1",
    id_formulario: "fenomeno-1",
    id_ciclo: 1,
    id_empresa: 1,
    titulo: "Análise de fenômeno",
    tipo: "ANALISE_FENOMENO",
    status: "ATIVO",
    campos: ["Sintoma", "Turno", "Local", "Condição"]
  },
  {
    id_formulario: "sigiloso-2",
    id_ciclo: 2,
    id_empresa: 2,
    titulo: "Formulário de outra empresa",
    tipo: "ANALISE_FENOMENO",
    status: "ATIVO"
  }
]);

acta.respostas_formulario.insertMany([
  {
    id_resposta: "resposta-fenomeno-2",
    id_formulario: "fenomeno-1",
    id_ciclo: 1,
    id_empresa: 1,
    id_usuario: 2,
    respondido_em: ISODate("2026-07-29T10:00:00Z"),
    respostas: [
      { pergunta: "Sintoma", resposta: "Retrabalho" },
      { pergunta: "Turno", resposta: "Noite" },
      { pergunta: "Local", resposta: "Linha A" },
      { pergunta: "Condição", resposta: "Temperatura alta" }
    ]
  },
  {
    id_resposta: "resposta-fenomeno-3",
    id_formulario: "fenomeno-1",
    id_ciclo: 1,
    id_empresa: 1,
    id_usuario: 3,
    respondido_em: ISODate("2026-07-30T14:00:00Z"),
    respostas: {
      Sintoma: "Retrabalho",
      Turno: "Noite",
      Local: "Linha A",
      Condição: "Temperatura alta"
    }
  },
  {
    id_formulario: "fenomeno-1",
    id_ciclo: 1,
    id_empresa: 1,
    id_usuario: 1,
    respondido_em: ISODate("2026-07-31T09:00:00Z"),
    respostas: {
      Sintoma: "Parada breve",
      Turno: "Manhã",
      Local: "Linha B",
      Condição: "Normal"
    }
  },
  {
    id_resposta: "resposta-sigilosa-2",
    id_formulario: "sigiloso-2",
    id_ciclo: 2,
    id_empresa: 2,
    respostas: { Segredo: "Não deve aparecer" }
  }
]);

acta.relatorios.insertMany([
  {
    id_relatorio: "relatorio-executivo-1-v1",
    id_ciclo: 1,
    id_empresa: 1,
    tipo: "RESUMO_EXECUTIVO",
    formato: "TEXTO",
    status: "CONCLUIDO",
    titulo: "Resumo executivo - Reduzir retrabalho",
    versao: 1,
    resumo: "Ciclo em execução com uma tarefa atrasada e uma bloqueada.",
    conteudo: {
      resumo_executivo: "O ciclo avança, mas exige atenção aos prazos das tarefas.",
      riscos: ["Tarefa Mapear processo atrasada", "Tarefa Validar padrão bloqueada"],
      proximos_passos: ["Tratar o bloqueio", "Revisar o prazo vencido"]
    },
    criado_por: 1,
    criado_em: ISODate("2026-07-30T10:00:00Z"),
    atualizado_em: ISODate("2026-07-30T10:00:00Z")
  },
  {
    id_relatorio: "relatorio-executivo-1-v2",
    id_ciclo: 1,
    id_empresa: 1,
    tipo: "RESUMO_EXECUTIVO",
    formato: "TEXTO",
    status: "CONCLUIDO",
    titulo: "Resumo executivo atualizado - Reduzir retrabalho",
    versao: 2,
    resumo: "Atualização executiva do ciclo.",
    conteudo: {
      resumo_executivo: "O retrabalho permanece como foco principal do ciclo.",
      pontos_relevantes: ["Padrão operacional em implantação"]
    },
    criado_por: 1,
    criado_em: ISODate("2026-07-31T10:00:00Z"),
    atualizado_em: ISODate("2026-07-31T10:00:00Z")
  },
  {
    id_relatorio: "relatorio-sigiloso-2",
    id_ciclo: 2,
    id_empresa: 2,
    tipo: "CICLO_COMPLETO",
    formato: "TEXTO",
    status: "CONCLUIDO",
    titulo: "Relatório confidencial",
    conteudo: { resumo_executivo: "Não deve aparecer para a empresa 1." },
    criado_por: 20,
    criado_em: ISODate("2026-07-31T11:00:00Z"),
    atualizado_em: ISODate("2026-07-31T11:00:00Z")
  }
]);
