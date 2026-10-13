# Autenticação e autorização

Em produção, cada requisição HTTP exige:

```http
Authorization: Bearer <ACTA_MCP_API_KEY>
X-Acta-Usuario-Id: 123
X-Acta-Empresa-Id: 45
X-Trace-Id: <uuid opcional>
```

O Bearer funciona como credencial entre serviços. O backend autenticado do ACTA
preenche os IDs; ferramentas MCP nunca recebem identidade ou empresa como argumento.

## Perfil e acesso

O MCP consulta `usuario_sistema` no PostgreSQL e exige que o usuário esteja ativo e
que `usuario_sistema.id_empresa` coincida com a empresa autenticada. O tipo persistido
`usuario_sistema.tipo_usuario` é mantido separado do nível de acesso para que a
autorização de escrita possa ser aplicada a cada ciclo.

| Perfil | Leitura | Criação e edição | Exclusão |
| --- | --- | --- | --- |
| `GESTOR` | Ciclos vinculados | Ciclos vinculados | Negada |
| Outros perfis vinculados | Ciclos vinculados | Negada | Negada |
| `ADMIN` | Ciclos da própria empresa, mesmo sem vínculo | Negada | Negada |

Cada chamada que acessa dados de ciclo recebe um `id_ciclo` inteiro e confirma no
PostgreSQL que o ciclo pertence à empresa autenticada. Perfis diferentes de `ADMIN`
precisam estar vinculados em `pdca.usuario_ciclo`. Um `GESTOR` só pode criar ou editar
quando também tem esse vínculo; `papel_ciclo` não concede permissão adicional.

O nível MCP `create` é uma barreira inicial para tools de escrita. A autorização final
de escrita é feita pelo serviço de domínio com o perfil consultado no banco e o ciclo
validado. Isso impede que `ADMIN` herde escrita apenas por seu nível global.

Tools de leitura de ciclo, incluindo respostas de formulários e contexto de relatório,
aceitam perfis não gestores que tenham acesso de leitura ao ciclo. Tools de
exclusão de dados de ciclo não são autorizadas por esta política.

Tools empresariais sem dados de ciclo, como `colaboradores_por_area`, permanecem
limitadas à empresa autenticada. Tools de FAQ consultam somente documentação pública.
Skills pessoais são gerenciadas pelo ACTA AI, fora do catálogo MCP.

O `usuario_id` continua sendo informado pelo backend; validar uma identidade Firebase
ou JWT de usuário final está fora desta mudança.

`ACTA_AUTH_MODE=disabled` é bloqueado quando `ACTA_ENV=production`.
