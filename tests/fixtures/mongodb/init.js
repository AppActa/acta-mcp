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
