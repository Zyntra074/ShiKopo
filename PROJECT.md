# Estado real do DreeZy-HUB — 2.1.0

Atualizado em 25/10/2026.

## Arquitetura implementada

A distribuição possui um arquivo principal único: RespawnHUD.lua. A modularização física proposta anteriormente não foi executada. Os blocos internos permanecem no principal, para manter a distribuição em um arquivo.

O runtime compartilhado possui:

- propriedade e encerramento de conexões, tarefas, desenhos e interfaces;
- jobs dinâmicos com frequência por função e perfil de desempenho;
- limpeza de falha de bootstrap e substituição de outra instância desta revisão;
- lista de jogadores invalidada por eventos e cache de amizade;
- normalização de teclado/mouse e tratamento de foco;
- erros limitados e diagnóstico opcional de custo;
- registro dos 12 blocos em Runtime.Modules para integração/diagnóstico.

O estado acessível fica em getgenv().DreeZyRuntime enquanto ativo. DreeZyHubLoaded só é marcado após a conclusão do bootstrap. Não são usados os contratos antigos de getgenv().DreezHub.Services/Modules como se já existissem.

## Blocos

MouseUnlocker, RespawnCore, TeamManager, AimbotCore, KillAuraCore, HitboxExpand, AutoShotCore, AutoClickerCore, ESPCore, HighAlertCore, MinimapCore e FreeShiftLockCore.

A interface e o ConfigManager ficam no mesmo arquivo. Existem cinco abas e 53 controles persistidos, além de atalhos e tecla de cursor.

## Situação das ações

| Ação | Estado |
|---|---|
| Recuperação do bootstrap e encerramento central | Implementado e testado no simulador |
| Correções funcionais da auditoria | Implementadas nos caminhos cobertos pelos testes |
| Trabalho sob demanda e limites de atualização | Implementado e comparado por contadores |
| Persistência com validação, backup e rollback | Implementado e testado |
| Remover execução remota da animação | Concluído |
| Reexecução após teleporte | Usa cópia local explícita, sujeita ao suporte do executor |
| Testes nativos Luau e integração completa | 143 casos aprovados e quatro fontes Lua compilados |
| Refatorar para arquivos modules/ e ui/ | Não implementado; não é pré-requisito desta revisão |
| Medição de FPS, física e permissões em jogo real | Não realizada |
| Confirmar origem e licença | Pendente de informação do autor |
| Publicação em GitHub | Revisão 2.1.0 e suíte de testes publicadas em Zyntra074/ShiKopo, main |

## Manutenção

Validar sintaxe com Luau nativo e executar tests/run_all.py após mudanças funcionais. Comparações do simulador são evidência de trabalho/ciclo de vida, sem substituir perfil de desempenho no cliente real.

Por solicitação explícita do proprietário em 25/10/2026, GitHub é a fonte oficial do script e cada alteração concluída e validada deve ser publicada em Zyntra074/ShiKopo, main. As orientações antigas para outro repositório foram substituídas. Cópias locais são temporárias para preparação e testes. A suíte completa está em tests/ e as evidências em reports/2026-10-25/.

