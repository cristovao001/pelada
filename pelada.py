import streamlit as st
import pandas as pd
from itertools import combinations

st.set_page_config(page_title="Tabela Pelada", layout="wide")

st.title("Tabela de Jogos da Pelada")

# Cores disponíveis
cores_disponiveis = ["Vermelho", "Azul", "Verde", "Amarelo", "Rosa", "Azul Claro", "Cinza", "Laranja"]

# Seleção do número de times
num_times = st.selectbox("Número de times:", [4, 5, 6])

# Nome dos times baseado na cor
st.subheader("Selecione a cor de cada time e os jogadores")
cores_selecionadas = []
info_times = {}

cols = st.columns(num_times)
for i in range(num_times):
    with cols[i]:
        cor = st.selectbox(f"Time {chr(65+i)} - Cor:", [c for c in cores_disponiveis if c not in cores_selecionadas], key=f"cor_{i}")
        integrantes = st.text_area(f"Jogadores do Time {cor}:", key=f"jogs_{i}")
        cores_selecionadas.append(cor)
        info_times[chr(65+i)] = {"cor": cor, "integrantes": integrantes, "pontos": 0, "saldo": 0, "gols_feitos": 0, "gols_sofridos": 0}

# Gerar confrontos
def gerar_confrontos(times):
    if num_times == 6:
        # Dividir em dois grupos fixos para simplicidade
        grupo_1 = list(times.keys())[:3]
        grupo_2 = list(times.keys())[3:]
        confrontos = [(a, b) for a, b in zip(grupo_1, grupo_2)] + \
                     [(grupo_1[0], grupo_2[1]), (grupo_1[1], grupo_2[0]), (grupo_1[0], grupo_2[2]),
                      (grupo_1[2], grupo_2[1]), (grupo_1[1], grupo_2[2]), (grupo_1[2], grupo_2[0])]
        return confrontos, grupo_1, grupo_2
    else:
        return list(combinations(times.keys(), 2)), None, None

confrontos, grupo_1, grupo_2 = gerar_confrontos(info_times)

# Tabela de confrontos
st.subheader("Confrontos")
resultados = []

for i, (time1, time2) in enumerate(confrontos):
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        g1 = st.number_input(f"Gols - {info_times[time1]['cor']}", min_value=0, key=f"g1_{i}")
    with col3:
        g2 = st.number_input(f"Gols - {info_times[time2]['cor']}", min_value=0, key=f"g2_{i}")
    resultados.append((time1, g1, time2, g2))

# Atualizar pontuação
def atualizar_tabela(resultados):
    for time in info_times:
        info_times[time].update({"pontos": 0, "saldo": 0, "gols_feitos": 0, "gols_sofridos": 0})
    for t1, g1, t2, g2 in resultados:
        info_times[t1]["gols_feitos"] += g1
        info_times[t1]["gols_sofridos"] += g2
        info_times[t2]["gols_feitos"] += g2
        info_times[t2]["gols_sofridos"] += g1
        info_times[t1]["saldo"] = info_times[t1]["gols_feitos"] - info_times[t1]["gols_sofridos"]
        info_times[t2]["saldo"] = info_times[t2]["gols_feitos"] - info_times[t2]["gols_sofridos"]
        if g1 > g2:
            info_times[t1]["pontos"] += 3
        elif g1 < g2:
            info_times[t2]["pontos"] += 3
        else:
            info_times[t1]["pontos"] += 1
            info_times[t2]["pontos"] += 1

atualizar_tabela(resultados)

def exibir_tabela(times):
    df = pd.DataFrame([
        {
            "Time": info_times[t]["cor"],
            "Pontos": info_times[t]["pontos"],
            "Saldo": info_times[t]["saldo"],
            "Gols Feitos": info_times[t]["gols_feitos"]
        }
        for t in times
    ])
    df = df.sort_values(by=["Pontos", "Saldo", "Gols Feitos"], ascending=False).reset_index(drop=True)
    df.index += 1
    return df

if num_times == 6:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Grupo 1")
        st.dataframe(exibir_tabela(grupo_1), use_container_width=True)
    with col2:
        st.markdown("### Grupo 2")
        st.dataframe(exibir_tabela(grupo_2), use_container_width=True)
else:
    st.markdown("### Classificação Geral")
    st.dataframe(exibir_tabela(info_times.keys()), use_container_width=True)

# Semifinais e finais
st.subheader("Fase Final")
if num_times == 6:
    df_grupo1 = exibir_tabela(grupo_1).head(2).copy()
    df_grupo2 = exibir_tabela(grupo_2).head(2).copy()
    classificados = pd.concat([df_grupo1, df_grupo2], ignore_index=True)
else:
    classificados = exibir_tabela(info_times.keys()).head(4).copy()

st.markdown("#### Semifinais")
col1, col2 = st.columns(2)
with col1:
    st.write(f"{classificados.iloc[0]['Time']} x {classificados.iloc[3]['Time']}")
    sf1_g1 = st.number_input("Gols SF1 - Time 1", min_value=0)
    sf1_g2 = st.number_input("Gols SF1 - Time 2", min_value=0)
with col2:
    st.write(f"{classificados.iloc[1]['Time']} x {classificados.iloc[2]['Time']}")
    sf2_g1 = st.number_input("Gols SF2 - Time 1", min_value=0)
    sf2_g2 = st.number_input("Gols SF2 - Time 2", min_value=0)

finalistas = []
if sf1_g1 > sf1_g2:
    finalistas.append(classificados.iloc[0]['Time'])
elif sf1_g2 > sf1_g1:
    finalistas.append(classificados.iloc[3]['Time'])
if sf2_g1 > sf2_g2:
    finalistas.append(classificados.iloc[1]['Time'])
elif sf2_g2 > sf2_g1:
    finalistas.append(classificados.iloc[2]['Time'])

if len(finalistas) == 2:
    st.markdown("#### Final")
    f_g1 = st.number_input("Gols Final - Time 1", min_value=0)
    f_g2 = st.number_input("Gols Final - Time 2", min_value=0)
    st.write(f"{finalistas[0]} x {finalistas[1]}")
    if f_g1 > f_g2:
        st.success(f"Campeão: {finalistas[0]}")
    elif f_g2 > f_g1:
        st.success(f"Campeão: {finalistas[1]}")
    elif f_g1 == f_g2 and f_g1 > 0:
        st.warning("Empate na final, decidir nos pênaltis!")
