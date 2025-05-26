from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from datetime import datetime
from rich import box
from rich.align import Align
from rich.style import Style
from rich.layout import Layout
from rich.padding import Padding
from core.database import check_fdj_status

console = Console()

def get_day_name(date_str):
    """Convertit une date en format texte en nom du jour."""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    return days[date_obj.weekday()]

def display_ascii_report(report, report_type):
    """Affiche un rapport au format ASCII avec des insights spéciaux."""
    # Vérifier le statut de la base FDJ
    fdj_status = check_fdj_status()
    fdj_color = "🟢" if fdj_status else "🔴"
    fdj_text = "Base FDJ à jour" if fdj_status else "Base FDJ non à jour"
    
    # Vérifier les insights spéciaux
    special_insights = []
    if report.get('lune_phase'):
        special_insights.append(f"🌙 Phase de lune: {report['lune_phase']}")
    if report.get('evenements_speciaux'):
        special_insights.extend([f"✨ {event}" for event in report['evenements_speciaux']])
    
    # En-tête
    print("\n" + "="*80)
    print(f"📊 RAPPORT {report_type.upper()} - {report['jeu']} {fdj_color} {fdj_text}")
    print(f"📅 Tirage de {report['jour_tirage']} {report['date']}")
    if special_insights:
        print("\n🌟 INSIGHTS SPÉCIAUX:")
        for insight in special_insights:
            print(f"  • {insight}")
    print("="*80)
    
    # Résumé
    print("\n📈 RÉSUMÉ")
    print(f"Cagnotte actuelle: {report['cagnotte']:,.2f} €")
    print(f"Gain brut total: {report['gains_bruts']:,.2f} €")
    print(f"Coût investi: {report['cout_investi']:,.2f} €")
    print(f"Gain net: {report['gain_net']:,.2f} €")
    print(f"Gain net cumulé: {report['gain_net_cumule']:,.2f} €")
    print(f"Ratio de gain: {report['ratio_gain']:.2%}")
    print(f"Indice de confiance global: {report['indice_confiance_global']:.2f}")
    
    # Analyse de tendance
    if 'analyse_tendance' in report:
        print("\n📊 ANALYSE DE TENDANCE")
        print(f"Tendance générale: {report['analyse_tendance']['tendance_generale']}")
        print(f"Force de la tendance: {report['analyse_tendance']['force_tendance']:.2f}")
        print(f"Période favorable: {report['analyse_tendance']['periode_favorable']}")
        print(f"Commentaire: {report['analyse_tendance']['commentaire']}")
    
    # Prédictions
    print("\n🎯 PRÉDICTIONS")
    for pred in report['predictions']:
        jackpot_symbol = "🍀" if pred.get('jackpot_predit', False) else ""
        print(f"Numéros: {', '.join(map(str, pred['numbers']))} | Spéciaux: {', '.join(map(str, pred['special']))}")
        print(f"Score: {pred['score']:.2f} | Confiance: {pred['indice_confiance']:.2f} | Gain Estimé: {pred['gain_estime']:,.2f} € {jackpot_symbol}")
        if 'commentaire' in pred:
            print(f"Commentaire: {pred['commentaire']}")
        print("-" * 40)
    
    # Gains Prédits
    print("\n💰 GAINS PRÉDITS")
    for i in range(len(report['gains_predits']['rangs'])):
        print(f"{report['gains_predits']['rangs'][i]}: {report['gains_predits']['gains'][i]:,.2f} € (Probabilité: {report['gains_predits']['probabilites'][i]:.2%})")
    
    # Historique
    print("\n📊 HISTORIQUE")
    for entry in report['historique']:
        print(f"{entry['date']}: {entry['gain']:,.2f} €")
        if 'commentaire' in entry:
            print(f"  • {entry['commentaire']}")
    
    print("\n" + "="*80)

    # Création du layout
    layout = Layout()
    layout.split_column(
        Layout(name="header"),
        Layout(name="body"),
        Layout(name="footer")
    )
    
    # Vérification du statut FDJ
    fdj_status = check_fdj_status(report['jeu'])
    status_color = "green" if fdj_status['is_up_to_date'] else "red"
    status_text = "✅ Base de données FDJ à jour" if fdj_status['is_up_to_date'] else "❌ Base de données FDJ non à jour"
    
    # En-tête avec logo, titre et statut
    if 'date' in report:
        day_name = get_day_name(report['date'])
        date_display = f"{day_name} {report['date']}"
    elif 'date_debut' in report:
        date_display = f"Période: {report['date_debut']} au {report['date_fin']}"
    else:
        date_display = f"Mois: {report['mois']}"
    
    header = Panel(
        Align.center(
            Text.assemble(
                ("🎲 LotoAIPredictor\n", "bold red"),
                (f"RAPPORT {report_type.upper()} - {report['jeu']}\n", "bold blue"),
                (date_display + "\n", "cyan"),
                (status_text, status_color)
            )
        ),
        box=box.DOUBLE,
        style="bold blue"
    )
    
    layout["header"].update(header)
    
    # Corps du rapport
    body_content = []
    
    # Statistiques
    if 'statistiques' in report:
        stats_table = Table(
            title="📊 Statistiques",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED
        )
        stats_table.add_column("Métrique", style="cyan")
        stats_table.add_column("Valeur", style="green")
        
        for key, value in report['statistiques'].items():
            stats_table.add_row(
                key.replace('_', ' ').title(),
                str(value)
            )
        
        body_content.append(stats_table)
    
    # Prédictions
    if 'predictions' in report:
        pred_table = Table(
            title="🎯 Prédictions",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED
        )
        pred_table.add_column("Grille", style="cyan")
        pred_table.add_column("Numéros", style="green")
        pred_table.add_column("Spéciaux", style="yellow")
        pred_table.add_column("Score", style="red")
        
        for i, pred in enumerate(report['predictions'], 1):
            pred_table.add_row(
                f"Grille {i}",
                ', '.join(map(str, pred['numbers'])),
                ', '.join(map(str, pred['special'])),
                str(pred['score_tendance'] + pred['score_correlation'] + pred['score_sequence'])
            )
        
        body_content.append(pred_table)
    
    # Recommandations
    if 'recommandations' in report:
        rec_table = Table(
            title="💡 Recommandations",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED
        )
        rec_table.add_column("Recommandation", style="cyan")
        
        for rec in report['recommandations']:
            rec_table.add_row(rec)
        
        body_content.append(rec_table)
    
    # Tendances
    if 'tendances' in report:
        trends_table = Table(
            title="📈 Tendances",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED
        )
        trends_table.add_column("Type", style="cyan")
        trends_table.add_column("Détails", style="green")
        
        for key, value in report['tendances'].items():
            if isinstance(value, dict):
                details = '\n'.join(f"{k}: {v}" for k, v in value.items())
            elif isinstance(value, list):
                details = '\n'.join(map(str, value))
            else:
                details = str(value)
            
            trends_table.add_row(
                key.replace('_', ' ').title(),
                details
            )
        
        body_content.append(trends_table)
    
    # Analyse de performance (pour les rapports mensuels)
    if 'analyse_performance' in report:
        perf_table = Table(
            title="📊 Analyse de Performance",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED
        )
        perf_table.add_column("Métrique", style="cyan")
        perf_table.add_column("Valeur", style="green")
        
        for key, value in report['analyse_performance'].items():
            perf_table.add_row(
                key.replace('_', ' ').title(),
                str(value)
            )
        
        body_content.append(perf_table)
    
    # Mise à jour du corps
    layout["body"].update(Padding(
        Panel(
            Align.center(
                Text.assemble(*[str(content) + "\n\n" for content in body_content])
            ),
            box=box.ROUNDED,
            style="bold blue"
        ),
        (1, 2)
    ))
    
    # Pied de page avec suggestion de mise à jour si nécessaire
    footer_content = [
        Text.assemble(
            ("🕒 ", "bold red"),
            (f"Rapport généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "cyan")
        )
    ]
    
    if not fdj_status['is_up_to_date']:
        footer_content.append(
            Text.assemble(
                ("\n⚠️ ", "bold yellow"),
                ("La base de données n'est pas à jour. Utilisez le bouton de mise à jour dans l'interface graphique.", "yellow")
            )
        )
    
    footer = Panel(
        Align.center(
            Text.assemble(*footer_content)
        ),
        box=box.DOUBLE,
        style="bold blue"
    )
    
    layout["footer"].update(footer)
    
    # Affichage du rapport
    console.print(layout) 