"""
Script pour générer les états financiers au format liasse officielle
À partir du fichier BALANCES_N_N1_N2.xlsx
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Ajouter le répertoire au path
sys.path.insert(0, os.path.dirname(__file__))

from etats_financiers import load_tableau_correspondance
from etats_financiers_v2 import (
    process_balance_to_liasse_format,
    generate_section_html_liasse,
    generate_css_liasse
)
from tableau_flux_tresorerie import calculer_tft
from annexes_liasse import calculer_annexes
from annexes_html import generate_annexes_html


def generer_etats_complets(fichier_excel="BALANCES_N_N1_N2.xlsx", output_dir=None):
    """
    Génère les états financiers complets au format liasse officielle
    
    Args:
        fichier_excel: Chemin vers le fichier Excel avec les 3 balances
        output_dir: Répertoire de sortie (par défaut: Bureau)
    """
    print("=" * 80)
    print("GÉNÉRATION ÉTATS FINANCIERS - FORMAT LIASSE OFFICIELLE")
    print("=" * 80)
    print()
    
    # Déterminer le répertoire de sortie
    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    
    # 1. Charger les balances
    print("1. Chargement des balances...")
    try:
        balance_n = pd.read_excel(fichier_excel, sheet_name="Balance N (2024)")
        balance_n1 = pd.read_excel(fichier_excel, sheet_name="Balance N-1 (2023)")
        print(f"   ✅ Balance N (2024): {len(balance_n)} comptes")
        print(f"   ✅ Balance N-1 (2023): {len(balance_n1)} comptes")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None
    
    # 2. Charger les correspondances
    print("\n2. Chargement des correspondances SYSCOHADA...")
    try:
        correspondances = load_tableau_correspondance()
        print(f"   ✅ Correspondances chargées")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None
    
    # 3. Traiter les balances au format liasse
    print("\n3. Traitement des balances au format liasse officielle...")
    try:
        results = process_balance_to_liasse_format(balance_n, balance_n1, correspondances)
        print(f"   ✅ Traitement terminé")
        print(f"      - Compte de Résultat: {len(results['compte_resultat'])} postes")
        print(f"      - Bilan Actif: {len(results['bilan_actif'])} postes")
        print(f"      - Bilan Passif: {len(results['bilan_passif'])} postes")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # 4. Calculer le TFT
    print("\n4. Calcul du Tableau des Flux de Trésorerie...")
    try:
        resultat_net_n = next((p['montant_n'] for p in results['compte_resultat'] if p['ref'] == 'XI'), 0)
        tft_data = calculer_tft(balance_n, balance_n1, resultat_net_n)
        results['tft'] = tft_data
        print(f"   ✅ TFT calculé")
        print(f"      - CAFG: {tft_data.get('cafg', 0):,.0f} FCFA")
        print(f"      - Variation trésorerie: {tft_data.get('variation_tresorerie', 0):,.0f} FCFA")
    except Exception as e:
        print(f"   ⚠️ TFT non calculé: {e}")
    
    # 5. Calculer les annexes
    print("\n5. Calcul des annexes...")
    try:
        # Convertir au format ancien pour les annexes
        results_ancien = {
            'bilan_actif': {p['ref']: {'ref': p['ref'], 'libelle': p['libelle'], 'montant': p['montant_n']} 
                           for p in results['bilan_actif']},
            'bilan_passif': {p['ref']: {'ref': p['ref'], 'libelle': p['libelle'], 'montant': p['montant_n']} 
                            for p in results['bilan_passif']},
            'charges': {},
            'produits': {},
            'totaux': {
                'actif': sum(p['montant_n'] for p in results['bilan_actif']),
                'passif': sum(p['montant_n'] for p in results['bilan_passif']),
                'resultat_net': resultat_net_n
            }
        }
        annexes_data = calculer_annexes(results_ancien)
        results['annexes'] = annexes_data
        print(f"   ✅ Annexes calculées: {len(annexes_data)} notes")
    except Exception as e:
        print(f"   ⚠️ Annexes non calculées: {e}")
    
    # 6. Générer le HTML
    print("\n6. Génération du HTML...")
    try:
        html = generate_css_liasse()
        
        # En-tête
        html += """
        <div class='etats-fin-container' style='max-width: 1400px; margin: 0 auto;'>
            <div class='etats-fin-header' style='background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 30px; border-radius: 12px; text-align: center; margin-bottom: 20px;'>
                <h1 style='margin: 0 0 10px 0; font-size: 28px;'>📊 ÉTATS FINANCIERS SYSCOHADA RÉVISÉ</h1>
                <p style='margin: 0; font-size: 16px; opacity: 0.9;'>Format Liasse Officielle - Exercices N et N-1</p>
            </div>
        """
        
        # Bilan
        html += "<h2 style='color: #1e3a8a; margin: 30px 0 15px 0; padding-bottom: 10px; border-bottom: 3px solid #3b82f6;'>BILAN</h2>"
        html += generate_section_html_liasse("bilan_actif", "🏢 ACTIF", results['bilan_actif'], "EXERCICE N (2024)", "EXERCICE N-1 (2023)")
        html += generate_section_html_liasse("bilan_passif", "🏛️ PASSIF", results['bilan_passif'], "EXERCICE N (2024)", "EXERCICE N-1 (2023)")
        
        # Compte de Résultat
        html += "<h2 style='color: #1e3a8a; margin: 30px 0 15px 0; padding-bottom: 10px; border-bottom: 3px solid #3b82f6;'>COMPTE DE RÉSULTAT</h2>"
        html += generate_section_html_liasse("compte_resultat", "📊 COMPTE DE RÉSULTAT", results['compte_resultat'], "EXERCICE N (2024)", "EXERCICE N-1 (2023)")
        
        # TFT
        if 'tft' in results and results['tft']:
            html += "<h2 style='color: #1e3a8a; margin: 30px 0 15px 0; padding-bottom: 10px; border-bottom: 3px solid #3b82f6;'>TABLEAU DES FLUX DE TRÉSORERIE</h2>"
            html += generate_tft_html_simple(results['tft'])
        
        # Annexes
        if 'annexes' in results and results['annexes']:
            html += "<h2 style='color: #1e3a8a; margin: 30px 0 15px 0; padding-bottom: 10px; border-bottom: 3px solid #3b82f6;'>ANNEXES</h2>"
            html += generate_annexes_html(results['annexes'])
        
        html += "</div>"
        
        # Script pour les accordéons
        html += """
        <script>
        document.querySelectorAll('.section-header-ef').forEach(header => {
            header.addEventListener('click', function() {
                this.classList.toggle('active');
                const content = this.nextElementSibling;
                content.classList.toggle('active');
            });
        });
        </script>
        """
        
        print(f"   ✅ HTML généré ({len(html)} caractères)")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # 7. Sauvegarder le fichier
    print("\n7. Sauvegarde du fichier...")
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Etats_Financiers_Liasse_{timestamp}.html"
        output_path = os.path.join(output_dir, filename)
        
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>États Financiers - Format Liasse Officielle</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 20px; background: #f5f5f5; font-family: 'Segoe UI', Arial, sans-serif;">
{html}
</body>
</html>"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"   ✅ Fichier sauvegardé: {output_path}")
        return output_path
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return None


def generate_tft_html_simple(tft_data):
    """Génère un HTML simple pour le TFT"""
    html = """
    <div style='background: white; padding: 20px; border-radius: 8px; margin: 10px 0; border: 1px solid #e5e7eb;'>
        <table style='width: 100%; border-collapse: collapse;'>
            <thead>
                <tr style='background: #f3f4f6;'>
                    <th style='padding: 12px; text-align: left; border: 1px solid #e5e7eb;'>LIBELLÉ</th>
                    <th style='padding: 12px; text-align: right; border: 1px solid #e5e7eb; width: 200px;'>MONTANT</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Flux opérationnels
    html += "<tr style='background: #dbeafe; font-weight: 700;'><td colspan='2' style='padding: 10px; border: 1px solid #e5e7eb;'>FLUX DE TRÉSORERIE DES ACTIVITÉS OPÉRATIONNELLES</td></tr>"
    for item in tft_data.get('flux_operationnels', []):
        montant = f"{item['montant']:,.0f}".replace(',', ' ') if item['montant'] != 0 else "-"
        html += f"<tr><td style='padding: 8px; border: 1px solid #e5e7eb;'>{item['libelle']}</td><td style='padding: 8px; text-align: right; border: 1px solid #e5e7eb; font-family: monospace;'>{montant}</td></tr>"
    
    # Flux d'investissement
    html += "<tr style='background: #dbeafe; font-weight: 700;'><td colspan='2' style='padding: 10px; border: 1px solid #e5e7eb;'>FLUX DE TRÉSORERIE DES ACTIVITÉS D'INVESTISSEMENT</td></tr>"
    for item in tft_data.get('flux_investissement', []):
        montant = f"{item['montant']:,.0f}".replace(',', ' ') if item['montant'] != 0 else "-"
        html += f"<tr><td style='padding: 8px; border: 1px solid #e5e7eb;'>{item['libelle']}</td><td style='padding: 8px; text-align: right; border: 1px solid #e5e7eb; font-family: monospace;'>{montant}</td></tr>"
    
    # Flux de financement
    html += "<tr style='background: #dbeafe; font-weight: 700;'><td colspan='2' style='padding: 10px; border: 1px solid #e5e7eb;'>FLUX DE TRÉSORERIE DES ACTIVITÉS DE FINANCEMENT</td></tr>"
    for item in tft_data.get('flux_financement', []):
        montant = f"{item['montant']:,.0f}".replace(',', ' ') if item['montant'] != 0 else "-"
        html += f"<tr><td style='padding: 8px; border: 1px solid #e5e7eb;'>{item['libelle']}</td><td style='padding: 8px; text-align: right; border: 1px solid #e5e7eb; font-family: monospace;'>{montant}</td></tr>"
    
    # Variation de trésorerie
    variation = tft_data.get('variation_tresorerie', 0)
    variation_str = f"{variation:,.0f}".replace(',', ' ')
    html += f"<tr style='background: #f0f9ff; font-weight: 700; font-size: 16px;'><td style='padding: 12px; border: 2px solid #3b82f6;'>VARIATION DE TRÉSORERIE</td><td style='padding: 12px; text-align: right; border: 2px solid #3b82f6; font-family: monospace; color: #1e3a8a;'>{variation_str}</td></tr>"
    
    html += """
            </tbody>
        </table>
    </div>
    """
    return html


if __name__ == "__main__":
    import sys
    
    # Vérifier les arguments
    fichier = "BALANCES_N_N1_N2.xlsx"
    if len(sys.argv) > 1:
        fichier = sys.argv[1]
    
    # Générer les états
    output_path = generer_etats_complets(fichier)
    
    if output_path:
        print("\n" + "=" * 80)
        print("✅ GÉNÉRATION TERMINÉE AVEC SUCCÈS")
        print("=" * 80)
        print(f"\n📂 Fichier: {output_path}\n")
        
        # Ouvrir le fichier
        try:
            import webbrowser
            webbrowser.open(output_path)
            print("🌐 Fichier ouvert dans le navigateur\n")
        except:
            print("⚠️ Impossible d'ouvrir automatiquement le fichier\n")
    else:
        print("\n" + "=" * 80)
        print("❌ ERREUR LORS DE LA GÉNÉRATION")
        print("=" * 80)
        sys.exit(1)
