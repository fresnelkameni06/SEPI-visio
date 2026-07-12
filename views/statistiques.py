import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from database import get_db_as_df

DB_NAME = "visio_database.db"

FEATURES = ["dark_ratio", "entropy", "zone_variance", "bottom_edge_density",
            "green_ratio", "ground_clutter", "edge_density", "texture",
            "brightness", "contrast", "saturation", "colorfulness",
            "file_size", "width", "height", "ai_confidence"]

FEATURE_LABELS = {
    "dark_ratio": "Ratio pixels sombres", "entropy": "Entropie (complexité)",
    "zone_variance": "Variance entre zones", "bottom_edge_density": "Contours au sol",
    "green_ratio": "Proportion de vert", "ground_clutter": "Désordre au sol",
    "edge_density": "Densité de contours", "texture": "Texture (rugosité)",
    "brightness": "Luminosité", "contrast": "Contraste", "saturation": "Saturation",
    "colorfulness": "Colorimétrie", "file_size": "Taille fichier (o)",
    "width": "Largeur (px)", "height": "Hauteur (px)", "ai_confidence": "Confiance IA (%)",
}

# features de la règle (pour le graphe d'importance)
RULE_FEATURES = ["dark_ratio", "bottom_edge_density", "zone_variance", "entropy", "green_ratio"]

PALETTE = {"vide": "#2ca02c", "pleine": "#d62728"}


def _prepare(df):
    df = df.copy()
    for col in FEATURES:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _annotated(df):
    d = df[df["manual_annotation"].notna() & (df["manual_annotation"].astype(str).str.strip() != "")]
    return d


def _present_features(df):
    return [f for f in FEATURES if f in df.columns and df[f].notna().any()]


def show():
    st.title("Statistiques & Visualisations")

    df_raw = get_db_as_df()
    st.metric("Nombre d'images analysées", len(df_raw))

    if len(df_raw) == 0:
        st.info("Aucune image en base pour le moment.")
        return

    df = _prepare(df_raw)
    features = _present_features(df)

    tabs = st.tabs([
        "Répartition", "Distributions par état", "Corrélations",
        "Importance des features", "Performance IA", "Couleurs moyennes",
    ])

    # 1 — RÉPARTITION (camembert Vide/Pleine sur prédiction IA)
    with tabs[0]:
        st.subheader("Répartition des états détectés par l'IA")
        counts = df["ai_annotation"].value_counts()
        if len(counts):
            c1, c2 = st.columns([1, 1])
            with c1:
                fig, ax = plt.subplots()
                colors = [PALETTE.get(str(k).lower(), "#888") for k in counts.index]
                ax.pie(counts.values, labels=counts.index, autopct="%1.0f%%",
                       colors=colors, startangle=90)
                ax.axis("equal")
                st.pyplot(fig)
            with c2:
                for label, n in counts.items():
                    st.metric(str(label), n, f"{100*n/counts.sum():.0f} %")
        else:
            st.info("Pas encore de prédictions IA.")

    # 2 — DISTRIBUTIONS PAR ÉTAT (box plot + histogramme)
    with tabs[1]:
        st.subheader("Comment chaque feature se répartit selon l'état")
        st.caption("Si les deux couleurs se séparent, la feature distingue bien Vide de Pleine.")
        base = df[df["ai_annotation"].notna()]
        palette = {c: PALETTE.get(str(c).lower(), None) for c in base["ai_annotation"].unique()}
        feat = st.selectbox("Feature", features,
                            format_func=lambda x: FEATURE_LABELS.get(x, x))
        sub = base[["ai_annotation", feat]].dropna()
        if len(sub):
            c1, c2 = st.columns(2)
            with c1:
                fig, ax = plt.subplots()
                sns.boxplot(data=sub, x="ai_annotation", y=feat, ax=ax, palette=palette)
                ax.set_xlabel("État détecté"); ax.set_ylabel(FEATURE_LABELS.get(feat, feat))
                st.pyplot(fig)
            with c2:
                fig, ax = plt.subplots()
                sns.histplot(data=sub, x=feat, hue="ai_annotation", kde=True,
                             palette=palette, ax=ax, element="step", common_norm=False)
                st.pyplot(fig)
            recap = sub.groupby("ai_annotation")[feat].agg(["mean", "median", "std", "count"])
            recap.columns = ["Moyenne", "Médiane", "Écart-type", "Effectif"]
            st.dataframe(recap.style.format("{:.3f}"))

    # 3 — CORRÉLATIONS (heatmap)
    with tabs[2]:
        st.subheader("Corrélations entre features")
        st.caption("Deux features très corrélées mesurent des choses proches (redondance).")
        corr = df[features].corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                    vmin=-1, vmax=1, ax=ax,
                    xticklabels=[FEATURE_LABELS.get(f, f) for f in features],
                    yticklabels=[FEATURE_LABELS.get(f, f) for f in features])
        st.pyplot(fig)

    # 4 — IMPORTANCE DES FEATURES (pouvoir de séparation seul)
    with tabs[3]:
        st.subheader("Pouvoir de séparation de chaque feature")
        st.caption("Accuracy obtenue avec cette seule feature (sur images annotées manuellement).")
        ann = _annotated(df)
        if len(ann) > 3:
            scores = {}
            for f in features:
                sub = ann[[f, "manual_annotation"]].dropna()
                if len(sub) < 3:
                    continue
                best = 0
                for t in sub[f].unique():
                    for d in (1, -1):
                        pred = (sub[f] > t) if d == 1 else (sub[f] < t)
                        acc = ((pred & (sub.manual_annotation == "Pleine")) |
                               (~pred & (sub.manual_annotation == "Vide"))).mean()
                        best = max(best, acc)
                scores[FEATURE_LABELS.get(f, f)] = best
            s = pd.Series(scores).sort_values()
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.barh(s.index, s.values, color="#2C5F2D")
            ax.set_xlabel("Accuracy avec cette seule feature")
            ax.axvline(0.5, color="gray", ls="--", lw=0.8)
            st.pyplot(fig)
        else:
            st.info("Il faut annoter manuellement quelques images (Vide/Pleine) pour calculer ceci.")

    # 5 — PERFORMANCE IA (matrice de confusion + métriques)
    with tabs[4]:
        st.subheader("Performance de la classification (IA vs annotation manuelle)")
        comp = _annotated(df).dropna(subset=["ai_annotation"])
        comp = comp[comp["ai_annotation"].astype(str).str.strip() != ""]
        if len(comp) > 0:
            tp = int(((comp.ai_annotation == "Pleine") & (comp.manual_annotation == "Pleine")).sum())
            tn = int(((comp.ai_annotation == "Vide") & (comp.manual_annotation == "Vide")).sum())
            fp = int(((comp.ai_annotation == "Pleine") & (comp.manual_annotation == "Vide")).sum())
            fn = int(((comp.ai_annotation == "Vide") & (comp.manual_annotation == "Pleine")).sum())
            total = tp + tn + fp + fn
            acc = (tp + tn) / total if total else 0
            prec = tp / (tp + fp) if (tp + fp) else 0
            rec = tp / (tp + fn) if (tp + fn) else 0
            spec = tn / (tn + fp) if (tn + fp) else 0
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0

            m = st.columns(5)
            m[0].metric("Accuracy", f"{acc:.0%}")
            m[1].metric("Précision", f"{prec:.0%}")
            m[2].metric("Recall", f"{rec:.0%}")
            m[3].metric("Spécificité", f"{spec:.0%}")
            m[4].metric("F1-score", f"{f1:.0%}")

            matrix = pd.DataFrame([[tp, fn], [fp, tn]],
                                  index=["Réel Pleine", "Réel Vide"],
                                  columns=["Prédit Pleine", "Prédit Vide"])
            fig, ax = plt.subplots()
            sns.heatmap(matrix, annot=True, fmt="d", cmap="Greens", ax=ax, cbar=False)
            st.pyplot(fig)
            st.caption(f"Calculé sur {total} images annotées manuellement.")
        else:
            st.info("Annotez manuellement des images pour comparer l'IA à la vérité terrain.")

    # 6 — COULEURS MOYENNES
    with tabs[5]:
        st.subheader("Couleur moyenne selon l'état")
        base = df[df["ai_annotation"].notna()]
        if all(c in df.columns for c in ["avg_r", "avg_g", "avg_b"]) and len(base):
            means = base.groupby("ai_annotation")[["avg_r", "avg_g", "avg_b"]].mean()
            cols = st.columns(len(means))
            for col, (label, row) in zip(cols, means.iterrows()):
                r, g, b = int(row.avg_r), int(row.avg_g), int(row.avg_b)
                col.markdown(f"**{label}**")
                col.markdown(f"<div style='background:rgb({r},{g},{b});height:80px;"
                             f"border-radius:8px;border:1px solid #ccc;'></div>",
                             unsafe_allow_html=True)
                col.caption(f"RGB({r},{g},{b})")