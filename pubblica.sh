#!/bin/bash
# Script per pubblicare aggiornamenti su Streamlit Cloud

echo "📦 Pubblicazione aggiornamenti..."
echo ""

# Vai nella cartella giusta
cd "$(dirname "$0")"

# Verifica modifiche
if [ -z "$(git status --porcelain)" ]; then
    echo "⚠️  Nessuna modifica da pubblicare."
    exit 0
fi

# Mostra cosa verrà pubblicato
echo "📝 Modifiche da pubblicare:"
git status --short
echo ""

# Chiedi messaggio commit
read -p "💬 Descrizione modifica: " msg

if [ -z "$msg" ]; then
    msg="Aggiornamento $(date '+%Y-%m-%d %H:%M')"
fi

# Commit e push
git add .
git commit -m "$msg"
git push

echo ""
echo "✅ Pubblicato! Il sito si aggiornerà in ~1 minuto."
echo "🌐 https://diagnosi-energetica.streamlit.app"
