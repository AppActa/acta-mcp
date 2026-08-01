# Autenticação e autorização

Em produção, cada requisição HTTP exige:

```http
Authorization: Bearer <ACTA_MCP_API_KEY>
X-Acta-Usuario-Id: 123
X-Acta-Empresa-Id: 45
X-Acta-Permissoes: read
X-Trace-Id: <uuid opcional>
```

O Bearer atual funciona como credencial entre serviços. Os IDs devem ser preenchidos pelo backend autenticado do ACTA, nunca por argumentos gerados pelo modelo. A evolução recomendada é substituir a chave estática por validação JWT/OAuth mantendo o mesmo `RequestContext`.

Todas as operações validam o ciclo, tarefa ou colaborador contra `empresa_id` antes de consultar dados. As queries também repetem o filtro de tenant, e os filtros MongoDB exigem simultaneamente aliases de ciclo e empresa.

`ACTA_AUTH_MODE=disabled` é bloqueado quando `ACTA_ENV=production`.

