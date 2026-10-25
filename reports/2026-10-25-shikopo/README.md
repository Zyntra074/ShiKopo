# ShiKopo 2.1.1 — validação da renomeação

Data: 25/10/2026. Base: bfa1717a8a3bed9742d3608ae75dce918b4dbffd, obtida do GitHub antes da edição.

O hub foi renomeado para ShiKopo no menu, boas-vindas, notificações, diagnóstico, objetos da interface, ações, runtime, arquivos de configuração, testes e documentação atual.

## Compatibilidade

Config.json, Config.json.bak e Favorites.json da pasta anterior são importados apenas quando o destino em ShiKopo/ ainda não existe. Os arquivos anteriores não são apagados nem alterados. Configurações continuam sendo carregadas manualmente. Uma falha de importação é registrada no diagnóstico.

A instância anterior com runtime compatível é encerrada antes da inicialização. Versões sem limpeza continuam exigindo reconexão. O script para reexecução após teleporte precisa ser atualizado em ShiKopo/RespawnHUD.lua; código antigo não é copiado automaticamente.

As referências antigas que permanecem no código ativo estão limitadas à compatibilidade e aos testes dessa compatibilidade. Créditos de origem e evidências históricas foram preservados. O arquivo principal mantém o nome RespawnHUD.lua para preservar a distribuição e os links existentes.

## Resultado

- Smoke: 18 casos aprovados.
- Challenger M1: 36 casos aprovados.
- Challenger probe: 20 casos aprovados.
- Challenger profundo: 10 casos aprovados.
- Regressões sintáticas: 7 casos aprovados.
- Integração: 59 casos aprovados, incluindo sete regressões da renomeação.
- Total: 150 casos aprovados, sem falhas; quatro fontes Lua compilados com Luau nativo.

Ambiente: Windows, Python 3.12.14, Lupa 2.8 e Luau 0.744. Os testes usam o script integral no simulador, sem rede. Não houve execução em cliente Roblox real nem nova medição de FPS.

Os arquivos *.log e results.json registram esta execução. manifest.json identifica os fontes e documentos atuais e as evidências desta revisão, exceto o próprio manifesto. Os relatórios anteriores são registros históricos e não foram reescritos.
