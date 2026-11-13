# 📊 Dashboard de Salários na Área de Dados

Dashboard interativo em **Python + Streamlit** que analisa quanto ganham profissionais de dados no mundo, por cargo, senioridade, modelo de trabalho, tamanho da empresa e país.

🔗 **App ao vivo:** [datascience1-dashboard-salarios-area-de-dados.streamlit.app](https://datascience1-dashboard-salarios-area-de-dados.streamlit.app/)

## 🎯 Perguntas de negócio

1. Qual é o salário típico de um profissional de dados, e como ele evoluiu de 2020 a 2025?
2. Quais cargos pagam mais?
3. Quanto pesa a senioridade no salário?
4. Trabalho remoto paga menos que presencial?
5. Como os salários variam entre países?

## 🗂️ Base de dados

`dados-imersao-final.csv`: **133.339 registros** de salários anuais (2020–2025), base usada na Imersão de Dados com Python da Alura.

| Coluna | Descrição |
|---|---|
| `ano` | Ano de referência do salário (2020–2025) |
| `senioridade` | Júnior, Pleno, Sênior ou Executivo |
| `contrato` | Integral, Parcial, Contrato ou Freelancer |
| `cargo` | Cargo do profissional (390 cargos distintos) |
| `salario` / `moeda` | Salário anual na moeda original |
| `usd` | Salário anual convertido para dólares (métrica principal) |
| `residencia` / `residencia_iso3` | País de residência (códigos ISO-2 e ISO-3) |
| `remoto` | Modelo de trabalho: Presencial, Híbrido ou Remoto |
| `empresa` | País sede da empresa |
| `tamanho_empresa` | Pequena, Média ou Grande |

**Limitações importantes**

- **~90% dos registros são de residentes nos EUA**, e cerca de 92% vêm de 2024–2025. Comparações entre países e com os anos de 2020–2021 têm amostras pequenas.
- **97% das empresas são classificadas como "Média"**, e os grupos Pequena e Híbrido são minoritários.
- Trata-se de uma pesquisa auto-declarada, não de uma amostra aleatória do mercado.

## 🧪 Metodologia

- **Mediana em vez de média:** salários têm distribuição assimétrica, com poucos valores muito altos (até US$ 800 mil), e a mediana representa melhor o profissional típico.
- **Amostra mínima:** rankings de cargos, destaques e linhas de tendência consideram apenas grupos com **pelo menos 30 registros**. No ranking de países o mínimo é 10.
- **Tamanho da amostra visível:** os gráficos mostram o número de registros de cada grupo ao passar o mouse.
- **Destaques dinâmicos:** os insights do topo são recalculados conforme os filtros.

## 💡 Principais insights (base completa)

- **Salário mediano:** US$ 146 mil por ano. Metade dos profissionais ganha entre US$ 106 mil e US$ 198 mil.
- **Senioridade:** a mediana sobe de **US$ 87 mil (Júnior)** para **US$ 130 mil (Pleno)**, **US$ 161 mil (Sênior)** e **US$ 190 mil (Executivo)**. Um Sênior ganha cerca de 1,9× um Júnior.
- **Cargos mais bem pagos** (≥ 30 registros): *Engineering Manager* (US$ 243 mil), *Head of AI* (US$ 239 mil) e *Head of Data* (US$ 209 mil).
- **Remoto × presencial:** praticamente a mesma mediana (US$ 145 mil × US$ 147 mil). O trabalho remoto não implica salário menor.
- **Evolução:** a mediana saltou de ~US$ 80 mil (2020) para ~US$ 145 mil (2023) e se estabilizou em 2024–2025. Parte desse salto reflete a mudança na composição da amostra.

## 🖥️ O que o dashboard oferece

- **Filtros:** período, senioridade, modelo de trabalho, contrato e tamanho da empresa
- **KPIs:** mediana com variação anual, faixa P25–P75, volume de registros e cargo mais bem pago
- **Abas:** Visão geral · Cargos · Perfil & trabalho · Geografia (mapa por cargo) · Dados (com download em CSV) · Sobre o projeto

## 🛠️ Tecnologias

Python · pandas · Plotly · Streamlit · Streamlit Community Cloud

## ▶️ Como executar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 👩‍💻 Autora

**Ana Condessa**, Analista de Dados · [GitHub](https://github.com/apcondessa)

Projeto desenvolvido a partir da Imersão de Dados com Python (Alura) e expandido com foco em análise para tomada de decisão.
