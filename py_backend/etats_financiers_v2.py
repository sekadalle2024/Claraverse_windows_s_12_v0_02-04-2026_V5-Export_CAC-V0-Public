"""
Module pour générer les états financiers avec format liasse officielle
- Affichage de TOUS les postes (même vides)
- 2 colonnes: Exercice N et Exercice N-1
- Format tableau conforme à la liasse officielle
"""

import pandas as pd
import json
import os
import re
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger("etats_financiers_v2")


def format_montant_liasse(montant: float) -> str:
    """
    Formate un montant pour la liasse officielle.
    Retourne "-" si montant est nul ou proche de zéro.
    """
    if abs(montant) < 0.01:
        return "-"
    return f"{montant:,.0f}".replace(',', ' ')


def load_structure_liasse_complete() -> Dict:
    """Charge la structure complète de la liasse officielle"""
    file_path = os.path.join(os.path.dirname(__file__), "structure_liasse_complete.json")
    
    if not os.path.exists(file_path):
        logger.warning(f"Structure liasse complète non trouvée: {file_path}")
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculer_poste_formule(ref: str, formule: str, postes_calcules: Dict[str, float]) -> float:
    """
    Calcule un poste de totalisation à partir d'une formule.
    Exemple: "TA - RA - RB" ou "XA + TE + TF"
    """
    try:
        # Remplacer les références par les valeurs (0 si absent)
        expression = formule
        for ref_poste in set(re.findall(r'[A-Z]{2}', formule)):
            valeur = postes_calcules.get(ref_poste, 0)
            expression = expression.replace(ref_poste, str(valeur))
        
        # Évaluer l'expression
        resultat = eval(expression)
        return float(resultat)
    except Exception as e:
        logger.error(f"Erreur calcul formule {ref} ({formule}): {e}")
        return 0.0


def process_balance_to_liasse_format(
    balance_n_df: pd.DataFrame,
    balance_n1_df: Optional[pd.DataFrame],
    correspondances: Dict
) -> Dict[str, Any]:
    """
    Traite les balances N et N-1 et génère les états au format liasse officielle.
    
    Returns:
        Dict avec structure:
        {
            'compte_resultat': [
                {
                    'ref': 'TA',
                    'libelle': 'Ventes de marchandises',
                    'note': '21',
                    'montant_n': 1000000,
                    'montant_n1': 950000
                },
                ...
            ],
            'bilan_actif': [...],
            'bilan_passif': [...]
        }
    """
    from etats_financiers import (
        detect_balance_columns,
        clean_number,
        match_compte_to_poste
    )
    
    # Charger la structure complète
    structure_complete = load_structure_liasse_complete()
    
    # Détecter les colonnes
    col_map_n = detect_balance_columns(balance_n_df)
    col_map_n1 = detect_balance_columns(balance_n1_df) if balance_n1_df is not None else None
    
    # Fonction pour calculer les montants d'une balance
    def calculer_montants_balance(balance_df, col_map, correspondances_section):
        """Calcule les montants pour une balance donnée"""
        montants = {}
        
        for idx, row in balance_df.iterrows():
            numero = str(row.get(col_map['numero'], '')).strip()
            if not numero or numero == 'nan' or not numero[0].isdigit():
                continue
            
            solde_debit = clean_number(row.get(col_map['solde_debit'], 0)) if col_map['solde_debit'] else 0
            solde_credit = clean_number(row.get(col_map['solde_credit'], 0)) if col_map['solde_credit'] else 0
            solde_net = solde_debit - solde_credit
            
            # Chercher correspondance
            for poste in correspondances_section:
                for racine in poste.get('racines', []):
                    if numero.startswith(racine):
                        ref = poste['ref']
                        if ref not in montants:
                            montants[ref] = 0
                        
                        # Appliquer le sens selon le type
                        type_poste = poste.get('type', '')
                        if type_poste == 'charge' or type_poste == 'actif':
                            montants[ref] += solde_net
                        elif type_poste == 'produit' or type_poste == 'passif':
                            montants[ref] += -solde_net
                        else:
                            montants[ref] += solde_net
                        break
        
        return montants
    
    # Traiter le Compte de Résultat
    resultat_complet = []
    
    if 'compte_resultat' in structure_complete:
        # Calculer montants N
        montants_n = calculer_montants_balance(
            balance_n_df,
            col_map_n,
            structure_complete['compte_resultat']
        )
        
        # Calculer montants N-1
        montants_n1 = {}
        if balance_n1_df is not None and col_map_n1:
            montants_n1 = calculer_montants_balance(
                balance_n1_df,
                col_map_n1,
                structure_complete['compte_resultat']
            )
        
        # Construire la liste complète avec TOUS les postes
        for poste in structure_complete['compte_resultat']:
            ref = poste['ref']
            
            # Si c'est un poste de totalisation, calculer avec la formule
            if poste.get('type') == 'total' and 'formule' in poste:
                montant_n = calculer_poste_formule(ref, poste['formule'], montants_n)
                montant_n1 = calculer_poste_formule(ref, poste['formule'], montants_n1) if montants_n1 else 0
                
                # Stocker pour les calculs suivants
                montants_n[ref] = montant_n
                montants_n1[ref] = montant_n1
            else:
                montant_n = montants_n.get(ref, 0)
                montant_n1 = montants_n1.get(ref, 0)
            
            resultat_complet.append({
                'ref': ref,
                'libelle': poste['libelle'],
                'note': poste.get('note', ''),
                'montant_n': montant_n,
                'montant_n1': montant_n1
            })
    
    # Traiter le Bilan (utiliser les correspondances existantes)
    bilan_actif_complet = []
    bilan_passif_complet = []
    
    # Pour le bilan, on utilise les correspondances existantes
    for section_name in ['bilan_actif', 'bilan_passif']:
        if section_name in correspondances:
            montants_n = calculer_montants_balance(
                balance_n_df,
                col_map_n,
                correspondances[section_name]
            )
            
            montants_n1 = {}
            if balance_n1_df is not None and col_map_n1:
                montants_n1 = calculer_montants_balance(
                    balance_n1_df,
                    col_map_n1,
                    correspondances[section_name]
                )
            
            liste_postes = bilan_actif_complet if section_name == 'bilan_actif' else bilan_passif_complet
            
            for poste in correspondances[section_name]:
                ref = poste['ref']
                liste_postes.append({
                    'ref': ref,
                    'libelle': poste['libelle'],
                    'note': '',
                    'montant_n': montants_n.get(ref, 0),
                    'montant_n1': montants_n1.get(ref, 0)
                })
    
    return {
        'compte_resultat': resultat_complet,
        'bilan_actif': bilan_actif_complet,
        'bilan_passif': bilan_passif_complet
    }


def generate_section_html_liasse(
    section_id: str,
    title: str,
    postes: List[Dict],
    exercice_n_label: str = "EXERCICE N",
    exercice_n1_label: str = "EXERCICE N-1"
) -> str:
    """
    Génère le HTML pour une section au format liasse officielle.
    Affiche TOUS les postes avec 2 colonnes de montants.
    """
    if not postes:
        return ''
    
    html = f"""
    <div class="etats-fin-section" data-section="{section_id}">
        <div class="section-header-ef">
            <span>{title}</span>
            <span class="arrow">›</span>
        </div>
        <div class="section-content-ef">
            <table class="liasse-table">
                <thead>
                    <tr>
                        <th style="width: 60px;">REF</th>
                        <th style="width: auto;">LIBELLÉS</th>
                        <th style="width: 60px;">NOTE</th>
                        <th style="width: 150px; text-align: right;">{exercice_n_label}</th>
                        <th style="width: 150px; text-align: right;">{exercice_n1_label}</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for poste in postes:
        ref = poste['ref']
        libelle = poste['libelle']
        note = poste.get('note', '')
        montant_n = poste.get('montant_n', 0)
        montant_n1 = poste.get('montant_n1', 0)
        
        # Déterminer si c'est un poste de totalisation (en majuscules généralement)
        is_total = ref.startswith('X') or libelle.isupper() or 'TOTAL' in libelle.upper()
        row_class = 'total-row' if is_total else ''
        
        html += f"""
                    <tr class="{row_class}">
                        <td class="ref-cell">{ref}</td>
                        <td class="libelle-cell">{libelle}</td>
                        <td class="note-cell">{note}</td>
                        <td class="montant-cell">{format_montant_liasse(montant_n)}</td>
                        <td class="montant-cell">{format_montant_liasse(montant_n1)}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    </div>
    """
    
    return html


def generate_css_liasse() -> str:
    """Génère le CSS pour le format liasse officielle"""
    return """
    <style>
    .liasse-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
    }
    
    .liasse-table thead {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
    }
    
    .liasse-table th {
        padding: 12px 8px;
        text-align: left;
        font-weight: 600;
        border: 1px solid #2563eb;
    }
    
    .liasse-table tbody tr {
        border-bottom: 1px solid #e5e7eb;
    }
    
    .liasse-table tbody tr:hover {
        background: #f9fafb;
    }
    
    .liasse-table tbody tr.total-row {
        background: #f0f9ff;
        font-weight: 700;
        border-top: 2px solid #3b82f6;
        border-bottom: 2px solid #3b82f6;
    }
    
    .liasse-table td {
        padding: 8px;
        border: 1px solid #e5e7eb;
    }
    
    .liasse-table .ref-cell {
        font-weight: 600;
        color: #1e3a8a;
        text-align: center;
    }
    
    .liasse-table .libelle-cell {
        color: #374151;
    }
    
    .liasse-table .note-cell {
        text-align: center;
        color: #6b7280;
        font-size: 11px;
    }
    
    .liasse-table .montant-cell {
        text-align: right;
        font-family: 'Consolas', 'Courier New', monospace;
        color: #059669;
        font-weight: 500;
    }
    
    .liasse-table .total-row .montant-cell {
        color: #1e3a8a;
        font-weight: 700;
    }
    </style>
    """
