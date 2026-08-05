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

## Níveis de acesso

`X-Acta-Permissoes` recebe um dos níveis abaixo. Cada nível inclui os anteriores:

| Nível | Capacidades |
| --- | --- |
| `read` | Consultar dados autorizados e gerenciar as próprias skills. |
| `create` | Ler, criar e atualizar dados operacionais. |
| `geral` | Ler, criar, atualizar e excluir; também libera formulários, treinamentos e o contexto consolidado de relatórios. |
| `admin` | Visão administrativa da empresa, sempre limitada ao `empresa_id` autenticado. |

O valor legado `write` é interpretado como `create` durante a migração. Permissões
desconhecidas são rejeitadas. Skills continuam privadas ao proprietário mesmo para
um administrador da empresa.

As tools `relatorios_contexto_ciclo`, `predicoes_respostas_atipicas` e
`predicoes_tema_formulario` também exigem `geral`, pois expõem ou processam
respostas de formulários de forma indireta.

Todas as operações validam o ciclo, tarefa ou colaborador contra `empresa_id` antes de consultar dados. As queries também repetem o filtro de tenant, e os filtros MongoDB exigem simultaneamente aliases de ciclo e empresa.

`ACTA_AUTH_MODE=disabled` é bloqueado quando `ACTA_ENV=production`.
