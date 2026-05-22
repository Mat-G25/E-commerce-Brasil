# 🛒 E-commerce Brasil — Dashboard Analítico

> Dashboard interativo para análise de mais de 100 mil pedidos do e-commerce brasileiro, construído com Python, SQLite e Streamlit.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.22-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white)

---

## Sobre o projeto

Este projeto transforma dados brutos do dataset público da **Olist** (maior plataforma de e-commerce do Brasil) em um dashboard visual e interativo, permitindo que qualquer pessoa — técnica ou não — extraia insights sobre o comportamento do mercado entre **2016 e 2018**.

O pipeline completo vai de arquivos CSV brutos até visualizações interativas:

```
CSVs (Kaggle) → SQLite (banco local) → Streamlit (dashboard web)
```

---

## Preview

![Dashboard Preview](https://raw.githubusercontent.com/Mat-G25/ecommerce-brasil/main/assets/preview.png)

---

## O que o dashboard mostra

| Seção | Descrição |
|---|---|
| **KPIs** | Pedidos entregues, receita total, ticket médio e avaliação média |
| **Receita Mensal** | Evolução da receita ao longo do tempo com área sombreada |
| **Status dos Pedidos** | Distribuição por status em gráfico de rosca |
| **Top 10 Categorias** | Categorias que mais faturaram no período |
| **Pedidos por Estado** | Concentração geográfica das vendas |
| **Avaliações** | Distribuição das notas com cores semafóricas (1⭐ a 5⭐) |

Todos os gráficos respondem ao **filtro de ano** na sidebar.

---

## Estrutura do projeto

```
ecommerce-brasil/
│
├── dashboard/
│   └── app.py              # Dashboard Streamlit
│
├── database/
│   └── load_data.py        # Script de carga dos CSVs para o SQLite
│
├── data/                   # CSVs do dataset Olist (não versionados)
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_customers_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_sellers_dataset.csv
│   └── ...
│
├── olist.db                # Banco SQLite gerado (não versionado)
├── requirements.txt
└── README.md
```

---

## Como rodar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/Mat-G25/ecommerce-brasil.git
cd ecommerce-brasil
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Baixe os dados

Faça o download do dataset no Kaggle:
 [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

Extraia os arquivos CSV dentro da pasta `data/`.

### 5. Popule o banco de dados

```bash
python database/load_data.py
```

### 6. Rode o dashboard

```bash
streamlit run dashboard/app.py
```

Acesse em: **http://localhost:8501**

---

## Tecnologias utilizadas

- **Python 3.12** — linguagem principal
- **Pandas** — manipulação e transformação dos dados
- **SQLite** — banco de dados local
- **Streamlit** — framework para o dashboard web
- **Plotly** — gráficos interativos

---

## Dataset

- **Fonte:** [Olist · Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **Período:** Setembro de 2016 a Outubro de 2018
- **Volume:** ~100 mil pedidos, ~200 mil registros de itens

---

## Autor

**Matheus Guimarães**
[github.com/Mat-G25](https://github.com/Mat-G25)