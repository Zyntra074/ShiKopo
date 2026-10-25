# ShiKopo 2.1.2 — arquivo principal ShiKopo.lua

Data: 25/10/2026. Base obtida do GitHub: 93fcea78a4b915e54bd4259c1a20564d9ebbabb8.

O arquivo principal foi renomeado de RespawnHUD.lua para ShiKopo.lua. Foram atualizados o cabeçalho, os links e instruções atuais, o caminho de reexecução após teleporte e os caminhos padrão dos testes e benchmark. O hub continua distribuído em um único arquivo principal, sem um carregador adicional no nome antigo.

A reexecução após teleporte requer a cópia atualizada em ShiKopo/ShiKopo.lua no espaço de arquivos do executor. Configurações e favoritos continuam nos mesmos caminhos ShiKopo/Config.json e ShiKopo/Favorites.json.

## Validação

- 150 casos aprovados: 18 smoke, 36 challenger M1, 20 probe, 10 deep, 7 regressões sintáticas e 59 de integração.
- Quatro fontes Lua compilados com Luau nativo, incluindo ShiKopo.lua.
- Verificados a ausência do arquivo principal antigo e os caminhos usados pelos testes e pela reexecução.
- Ambiente: Windows, Python 3.12.14, Lupa 2.8 e Luau 0.744.

Os testes usam o fonte integral no simulador, sem rede. Não houve execução no cliente Roblox real nem medição de FPS. Logs e results.json registram esta execução; manifest.json identifica fontes, documentos e evidências atuais, exceto o próprio manifesto. As pastas de relatórios anteriores permanecem como registros históricos.
