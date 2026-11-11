<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE) -->

<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-log.png" alt="Omega-Log" width="512">
</div>

# 📜 OMEGA-LOG

**Gerenciador e visualizador de logs de servidor**

> Desenvolvido por [kraynux](https://github.com/kraynux) para [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Página oficial: [OMEGA-LOG](https://kraynux.snake-mackarel.ts.net/omega-log/translation/pt-BR/) &nbsp; Visão geral: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-log/screenshots/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-Textual%20TUI-cyan.svg)](https://github.com/Textualize/textual)

🌐 Interface, documentação e exportações disponíveis em **17 idiomas**.  
**Idiomas:**
<img src="https://flagcdn.com/w20/fr.png" alt="France" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-log** é a ferramenta da suíte `omega-` dedicada ao gerenciamento, à leitura e à análise de arquivos de log de servidor em TUI — detecção automática dos serviços ativos e de seus logs, biblioteca central, três modos de leitura (acompanhamento simples, leitura clássica, mesclagem de vários arquivos via `lnav`), tratamento de IPs, estatísticas, rotação/backup/restauração, limpeza segura e exportação. Construído por **portabilidade e adaptação** do código já maduro do [omega-fire](https://github.com/kraynux) e do [omega-serv](https://github.com/kraynux), em vez de ser reescrito do zero.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/pt-BR/omega-log/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/pt-BR/omega-log/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/pt-BR/omega-log/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/pt-BR/omega-log/D.png" width="24%" />
</p>

## 1. Visão e escopo

O Omega-log responde a uma pergunta simples: "o que está acontecendo nos meus logs, e como eu cuido disso?" — sem depender de uma lista fixa de caminhos conhecidos, sem nunca rodar como root por padrão e sem nunca perder ou corromper silenciosamente um arquivo de log real.

### O que o Omega-log faz

- Detecta automaticamente os serviços ativos na máquina (servidores web, bancos de dados, e-mail, DNS, segurança, `omega-serv`...) e propõe a importação de seus logs conhecidos, um a um ou todos de uma vez — como complemento a uma varredura manual de qualquer pasta.
- Centraliza os logs a tratar em uma Biblioteca única, ponto de entrada de todas as outras telas.
- Lê um log em três modos, conforme a necessidade: acompanhamento simples com parsing e estatísticas, leitura clássica bruta com acompanhamento ao vivo, ou mesclagem de vários arquivos encapsulando o `lnav`.
- Memoriza combinações de logs + visualizador na forma de Favoritos, para uma abertura direta.
- Calcula o top 10 de IPs por período, ou pesquisa um IP específico, e permite sua remoção direcionada em um ou vários arquivos.
- Calcula estatísticas de acesso (volume, IPs únicos, taxa de erro, distribuição por hora) exportáveis em JSON ou HTML com tema.
- Faz backup (compressão + retenção automática), manualmente ou toda noite por meio dos backups agendados, restaura (mesclagem ou sobrescrita, com backup de segurança) e limpa (truncamento no local ou exclusão) os arquivos de log, sempre com confirmação explícita.
- Verifica a saúde dos logs (permissões, logs mudos ou danificados, espaço em disco, backups) e diz o que fazer em cada constatação.
- Adapta-se automaticamente às capacidades do terminal (cores, tamanho) via `omega-lib`, como o restante da suíte.

### O que o Omega-log não faz

| Função | Ferramenta responsável |
|---|---|
| Firewall, regras de rede, detecção de intrusão | OMEGA-FIRE |
| Servidor web, reverse proxy, WAF, Active Defense | OMEGA-SERV |
| Varredura de portas, identificação de serviços de rede | OMEGA-CHECK |
| Observação de rede, identidade digital de um alvo | OMEGA-TRACK |

Ainda não há CLI com paridade completa com a TUI (o modo de linha de comando atual cobre apenas a varredura de serviços, veja §3.2), nem agregação centralizada de várias máquinas, nem alertas em tempo real por limite — o Omega-log continua sendo uma ferramenta de inspeção e manutenção local, não um SIEM.

### Aviso de uso

As ações de manutenção (**Limpar**, **Rotate → Restaurar em modo Sobrescrever**) modificam ou apagam definitivamente o conteúdo real dos seus arquivos de log — sempre precedidas de uma confirmação explícita que detalha os arquivos envolvidos, nunca disparadas automaticamente. Em caso de dúvida, faça um backup (**Rotate → Fazer backup agora**) antes de agir.

## 2. Instalação

### Pré-requisitos

- Python 3.10+
- Linux (testado em Arch/Manjaro, Debian/Ubuntu, RHEL/Fedora)
- `lnav` instalado no sistema, apenas para o visualizador de mesclagem de vários arquivos (os outros dois visualizadores funcionam normalmente sem ele):

```bash
# Arch / Manjaro
sudo pacman -S lnav

# Debian / Ubuntu
sudo apt install lnav
```

### Instalação

```bash
[ -d omega-log ] && echo "ℹ️ Já extraído aqui, etapa ignorada." || tar -xzf omega-log-1.6.0.tar.gz
cd omega-log/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Cria o ambiente virtual `.venv` se ele ainda não existir.
2. Instala as dependências (primeiro o `omega-lib` embutido, se presente, depois `pip install -e .` — o `pyproject.toml` continua sendo a única fonte de verdade).
3. Torna `omega-log.sh` e `install.sh` executáveis.
4. Verifica a presença do `lnav` (aviso informativo se ausente, nunca bloqueante).
5. Adiciona o alias `log` ao `~/.bashrc` e ao `~/.zshrc` (sem duplicar se já existir).

### Dependências

Declaradas no `pyproject.toml` (sem `requirements.txt` separado):
- `omega-lib`: biblioteca compartilhada da suíte (temas TUI + exportação, detecção de terminal, armazenamento de configurações)
- `textual`: interface TUI
- `jinja2`: exportação HTML com tema (estatísticas, arquivos compactados)
- `pyte`: emulação de terminal para o visualizador `lnav` (renderização em um pty encapsulado)
- Dependências de desenvolvimento (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `ruff`, `mypy`

## 3. Uso

### 3.1. Modo interativo (TUI)

Recomendado para o uso diário — iniciado sem argumento:

```bash
./omega-log.sh
```
se você criou o alias, basta digitar `log` em um novo terminal:
```bash
log
```

Percurso geral: tela de inicialização → menu principal (duas colunas — Registro de capacidades/Biblioteca/Ver os logs/Favoritos/Ver e tratar IP/Estatísticas (acesso) de um lado, Rotate/Limpar/Exportar/Saúde dos logs/Opções/Ajuda do outro) → tela da função escolhida → volta ao menu (`Esc`). A ajuda completa (`a`) detalha cada tela, cada visualizador e os conceitos transversais (elevação sudo pontual, estados dos logs, seleção por números) — veja §4 para o essencial.

#### Atalhos de teclado

| Tecla | Ação |
|---|---|
| `↑` / `↓` | Navegar entre os elementos de uma tela |
| `Tab` / `Shift+Tab` | Navegar entre os campos de um formulário |
| `Esc` | Voltar à tela anterior (confirmação de saída na tela inicial) |
| `t` | Próximo tema (aplicado imediatamente, sem confirmação) |
| `r` | Atualizar a detecção do terminal |
| `a` | Exibir a ajuda (completa, um capítulo por tela) |
| `q` | Sair (com confirmação) |

### 3.2. Modo de linha de comando (CLI)

Ainda sem paridade completa com a TUI (favoritos, limpeza... virão com suas próprias fases, veja `plan_omega_log.md` §12):

```bash
# Detecta os serviços ativos e seus logs conhecidos
python -m omega_log scan

# + varredura manual de uma pasta adicional
python -m omega_log scan --path /var/log

# Versão instalada, e comparação com a última versão publicada
python -m omega_log version --check

# Backups agendados que venceram (executado toda noite pelo timer systemd ou pela crontab)
python -m omega_log rotate run-automations
```

### 3.3. Variáveis de ambiente

| Variável | Efeito |
|---|---|
| `OMEGA_LOG_VAR_DIR` | Altera o local da pasta de estado do aplicativo (`./var` por padrão, relativo à pasta de execução) |
| `OMEGA_LOG_LANG` | Força o idioma da interface para a sessão (ex.: `en`, `de`, `ja`) sem alterar a configuração salva |

## 4. Funcionalidades

| Tela | Descrição |
|---|---|
| **Registro de capacidades** | Detecta os serviços ativos na máquina e propõe a importação de seus logs conhecidos, um a um ou todos de uma vez. Varredura manual de uma pasta como complemento. |
| **Biblioteca** | Hub central que referencia todos os logs a tratar — alimentada pelo Registro, por importação manual, pelos logs conhecidos do Omega-Serv ou por uma cópia obtida via SSH. |
| **Ver os logs** | Seleção de um ou vários logs da Biblioteca + escolha do visualizador (1 log → os 3 visualizadores; 2+ logs → apenas `lnav`). |
| **Favoritos** | Combinações de logs + visualizador salvas com um nome, para uma abertura direta. |
| **Ver e tratar IP** | Top 10 de IPs por período (24h/7d/30d/tudo), ou pesquisa de um IP específico (IPv4 ou IPv6), e remoção direcionada de um IP em um ou vários logs. |
| **Estatísticas (acesso)** | Volume, IPs únicos, taxa de erro, top IPs, distribuição por hora — exportação JSON/HTML com 5 temas. |
| **Rotate** | Backup compactado de um log + retenção automática dos arquivos compactados excedentes + restauração (mesclagem ou sobrescrita, com backup de segurança). **Backups agendados**: um log salvo a cada dia, semana ou mês, executado toda noite por um timer systemd ou por uma linha da sua crontab (OpenRC, runit), na sua conta, nunca como root. |
| **Limpar** | Esvazia o conteúdo de um log (truncamento no local, seguro para um serviço que ainda o mantém aberto) ou exclui completamente um ou vários arquivos — sempre com confirmação. |
| **Exportar** | Exportação da lista de arquivos compactados (Rotate) em JSON ou HTML com tema. |
| **Saúde dos logs** | Verificação somente leitura dos logs da Biblioteca, do disco, dos backups e dos backups agendados: permissões, logs mudos ou danificados, datas, logrotate, dias até o disco encher, com a ação a tomar. Correção das permissões abertas demais (com sudo se necessário), exportação JSON/HTML/TXT. |
| **Opções** | Tema, perfil de renderização, idioma da interface e idioma das exportações (17 idiomas), limpeza das pastas do aplicativo (exports/screenshots). |

### Os 3 visualizadores

1. **Simples** — acompanhamento ao vivo com parsing genérico (data/hora, IP, nível, serviço) e mini-tabela de estatísticas. Para um access log HTTP reconhecido, colunas adicionais Código HTTP / latência, coloridas por limite.
2. **Clássico** — leitura das últimas linhas brutas + alternância "Acompanhar ao vivo", sem parsing: o mais simples e o mais confiável, qualquer que seja o formato.
3. **lnav** — mesclagem de vários arquivos em um terminal encapsulado (pty), para uma análise cruzada. Ciclo de tema (`t`), marcação + cópia para a área de transferência (`Ctrl+C`, OSC 52), saída (`Ctrl+Q`) — todos interceptados antes do próprio `lnav`.

## 5. Compatibilidade de terminais

A TUI (Textual) detecta automaticamente as capacidades do terminal (emulador, tamanho) e adapta sua folha de estilo estrutural de acordo (`complete`/`standard`/`reduced`/`mono`), sem flag manual — a mesma política compartilhada por toda a suíte `omega-` (`omega-lib`, `terminal/policies.py`). Pode ser atualizada ao vivo com a tecla `r`.

### Perfil conforme o emulador detectado

| Emulador | Perfil inicial |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderno | `reduced` |
| TTY Linux, SSH legado | `mono` |
| Emulador não reconhecido | `reduced` (alternativa padrão) |

### Perfil conforme o tamanho do terminal

| Tamanho mínimo (colunas × linhas) | Teto de perfil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| abaixo disso | `mono` |

O perfil final adotado é **o mais restritivo dos dois** (emulador e tamanho).

## 6. Arquitetura

Clean Architecture (domínio / aplicação / infraestrutura / interfaces), a mesma convenção do restante da suíte OMEGA:

```text
src/omega_log/
├── core/            Registro de capacidades (deteccao de servicos)
├── domain/          Logica de negocio pura (parsing, estatisticas, rotacao, limpeza)
├── ports/           Contratos (Protocol)
├── application/     Casos de uso
├── infrastructure/  Implementacoes reais (probes, armazenamento, arquivos compactados, exportacao, lnav, concorrencia)
├── interfaces/      TUI (Textual) + CLI
└── app/             Composition root
```

Depende do [`omega-lib`](../../../../LIB/omega-lib) para o tema (10 temas TUI + 5 temas de exportação), a detecção de terminal e o armazenamento de configurações — a mesma base do restante da suíte. Os cálculos pesados (top IPs, estatísticas de acesso) são executados em um `ProcessPoolExecutor` dedicado (`infrastructure/concurrency/`), nunca na thread da interface, para continuar responsivo mesmo em um arquivo de várias centenas de milhares de linhas.

## 7. Testes

```bash
source .venv/bin/activate
pytest tests/ -q      # 243 testes
ruff check .
mypy src
```

Estrutura: `tests/unit/` (domínio e aplicação, sem I/O real), `tests/integration/` (arquivos reais, TUI headless via a API `Pilot` do Textual).

## 8. Estado do desenvolvimento

As 10 fases do plano de desenvolvimento estão concluídas: base, domínio, TUI básica, visualizadores, favoritos/biblioteca/IP, manutenção, estatísticas/exportação, finalização, elevação sudo pontual, cálculos CPU-bound transferidos para um processo separado — veja `plan_omega_log.md` para o detalhe de cada decisão de portabilidade. Desde a 1.6.0, as novidades do gerenciador de logs do omega-serv 2.6.0 foram incorporadas: Saúde dos logs, backups agendados, pesquisa de um IP específico, versão exibida e verificação de atualizações.

## 9. Licença

MIT — veja [LICENSE](../../../LICENSE).

---

> Omega-log — Detectar, centralizar, ler, analisar, manter.
> Seus logs continuam sendo seus: nenhuma elevação de privilégio sem necessidade real, nenhuma ação destrutiva sem confirmação.
