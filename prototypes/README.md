# Protótipo visual do ShiKopo

Proposta de interface preparada em 25/10/2026 a partir do vídeo e das capturas fornecidos pelo proprietário. A referência orienta a organização e a linguagem visual; não foi copiado código do Matcha e nenhuma captura ou gravação pessoal foi publicada.

## Entrega

- `shikopo-workspace.html`: fragmento autocontido para a prévia interativa no Codex, com duas variantes completas.
- `validation.json`: resultados das verificações no navegador.

**Workspace** usa navegação lateral e uma área de controle mais próxima de um aplicativo. **Compacto** usa abas superiores e barra flutuante, seguindo a organização compacta da referência.

A prévia inclui Personagem, Visuais, Mundo, Jogadores, Combate, Biblioteca, Perfis e Opções. Os controles de voo, noclip, velocidade, iluminação, ESP, teleporte, espectador, waypoints, atalhos e perfis alteram apenas o estado e a cena demonstrativa. Jogadores e NPCs são fictícios. O editor recebe rascunhos e simula uma execução sem avaliar ou enviar código.

## Situação da implementação

Esta é uma proposta visual para aprovação antes da reformulação Luau. O arquivo de uso `ShiKopo.lua` permanece na versão 2.1.2. Os controles novos da prévia não foram adicionados ao runtime Roblox nesta etapa.

A biblioteca distingue recursos atuais, como ESP, High Alert, minimapa e teleporte, de propostas, como voo, noclip e espectador. Isso descreve o catálogo visual; não constitui verificação adicional da implementação ou compatibilidade em jogos reais.

## Validação

Foram verificados os dois layouts e os fluxos de controles, captura de atalho, busca/seleção de jogadores, teleporte e espectador simulados, ações com NPC, criação de waypoints, salvamento e carga de perfis, simulação do editor, aparência, parada de módulos e minimizar/restaurar. As oito áreas dos dois layouts foram inspecionadas em larguras de conteúdo de 1024, 768, 375 e 320 px, totalizando 64 combinações. Nenhum erro JavaScript nem transbordamento horizontal foi detectado. Também houve inspeção visual das telas de desktop e celular.

O fragmento não realiza chamadas de rede e usa os ícones e a navegação entre variantes fornecidos pela prévia do Codex quando disponíveis. O estado interativo é mantido no host por `widgetState/setWidgetState`, com funcionamento local quando essas APIs não existem. Para exportação ou hospedagem futura, será necessário produzir uma página independente e definir a persistência correspondente.

## Evolução sugerida

1. Aprovar o layout e os fluxos deste protótipo.
2. Portar os componentes da interface para o runtime Luau, conectando primeiro os recursos existentes.
3. Implementar e validar cada nova funcionalidade no simulador e em ambiente Roblox apropriado, sem prometer suporte universal.
4. Estudar separadamente um aplicativo Windows para perfis, escolha e abertura de executor. A integração automática depende das interfaces e do suporte oferecidos pelo executor escolhido; este protótipo não implementa injeção nem essa integração.
