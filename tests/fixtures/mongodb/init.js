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

acta.perdas_ganhos.insertOne({
  id_ciclo: 1,
  id_empresa: 1,
  perdas: [{ descricao: "Horas de retrabalho", impacto: 120 }],
  ganhos: [{ descricao: "Padronização", impacto: 80 }]
});

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

