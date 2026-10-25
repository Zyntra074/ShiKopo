# ShiKopo / DreeZy-HUB

## Repositório e publicação

- O repositório oficial deste trabalho é https://github.com/Zyntra074/ShiKopo, branch `main`.
- Por solicitação explícita do proprietário em 25/10/2026, o GitHub é a fonte oficial do script. Comece cada alteração pela versão atual do GitHub e publique cada mudança concluída e validada, com sua documentação e testes correspondentes.
- Cópias locais servem somente como preparação temporária e ambiente de validação. Não mantenha uma versão independente em Downloads nem entregue uma alteração somente local como concluída.
- Use exclusivamente `Zyntra074/ShiKopo`; referências antigas a outros repositórios foram substituídas por esta orientação.
- Antes de publicar, confira a revisão atual de `main`, preserve mudanças concorrentes e faça atualização normal, sem sobrescrever o histórico.
- Não inclua ambientes virtuais, executáveis, configurações pessoais nem arquivos temporários de depuração.

## Validação

- Preserve a distribuição principal em `RespawnHUD.lua`, salvo pedido do proprietário para mudar a estrutura.
- Após mudanças funcionais no script, valide a sintaxe com Luau nativo e execute `python tests/run_all.py` com Python 3.12, Lupa 2.8 e Luau 0.744. Consulte `TEST_INFRA.md` para preparar o ambiente.
- Diferencie resultados do simulador de medições no Roblox real. Não afirme ganho de FPS ou compatibilidade com executores sem medição correspondente.
- Ao concluir, informe o commit publicado e o resultado das verificações. Se a publicação falhar, deixe essa pendência explícita.
