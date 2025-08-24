import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
import io
import base64
from datetime import datetime
import streamlit as st
from typing import Dict, List, Any
import tempfile
import os

class ReportGenerator:
    """Generate professional PDF and CSV reports for financial analysis"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.navy,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            spaceAfter=12,
            spaceBefore=12
        )
    
    def plotly_to_image(self, fig: go.Figure, width: int = 800, height: int = 600) -> str:
        """
        Convert Plotly figure to base64 image string
        
        Args:
            fig: Plotly figure
            width: Image width
            height: Image height
            
        Returns:
            Base64 encoded image string
        """
        try:
            img_bytes = pio.to_image(fig, format="png", width=width, height=height)
            img_base64 = base64.b64encode(img_bytes).decode()
            return img_base64
        except Exception as e:
            st.error(f"Error converting plot to image: {str(e)}")
            return ""
    
    def create_summary_table(self, data: Dict[str, Any], title: str = "Summary Statistics") -> Table:
        """
        Create a formatted table for the PDF report
        
        Args:
            data: Dictionary with key-value pairs
            title: Table title
            
        Returns:
            ReportLab Table object
        """
        # Prepare table data
        table_data = [['Metric', 'Value']]
        
        for key, value in data.items():
            if isinstance(value, float):
                if abs(value) < 0.01:
                    formatted_value = f"{value:.6f}"
                else:
                    formatted_value = f"{value:.4f}"
            elif isinstance(value, bool):
                formatted_value = "Yes" if value else "No"
            else:
                formatted_value = str(value)
            
            # Format key for display
            display_key = key.replace('_', ' ').title()
            table_data.append([display_key, formatted_value])
        
        # Create table
        table = Table(table_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        return table
    
    def generate_risk_analytics_report(self, analysis_results: Dict, 
                                     portfolio_name: str = "Portfolio") -> bytes:
        """
        Generate comprehensive risk analytics PDF report
        
        Args:
            analysis_results: Dictionary with risk analysis results
            portfolio_name: Name of the portfolio
            
        Returns:
            PDF bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Title
        title = Paragraph(f"Risk Analytics Report - {portfolio_name}", self.title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Report metadata
        report_date = datetime.now().strftime("%B %d, %Y at %H:%M")
        metadata = Paragraph(f"Generated on {report_date}", self.styles['Normal'])
        story.append(metadata)
        story.append(Spacer(1, 20))
        
        # Executive Summary
        summary_heading = Paragraph("Executive Summary", self.heading_style)
        story.append(summary_heading)
        
        # Risk metrics summary
        if 'var' in analysis_results:
            var_95 = analysis_results['var'].get(0.95, 0) * 100
            var_99 = analysis_results['var'].get(0.99, 0) * 100
            sharpe = analysis_results.get('sharpe_ratio', 0)
            max_dd = analysis_results.get('max_drawdown', 0) * 100
            
            summary_text = f"""
            <b>Key Risk Metrics:</b><br/>
            • Value at Risk (95%): {var_95:.2f}%<br/>
            • Value at Risk (99%): {var_99:.2f}%<br/>
            • Sharpe Ratio: {sharpe:.3f}<br/>
            • Maximum Drawdown: {abs(max_dd):.2f}%<br/>
            """
            
            summary_para = Paragraph(summary_text, self.styles['Normal'])
            story.append(summary_para)
            story.append(Spacer(1, 20))
        
        # Detailed metrics table
        metrics_heading = Paragraph("Detailed Risk Metrics", self.heading_style)
        story.append(metrics_heading)
        
        # Prepare detailed metrics
        detailed_metrics = {}
        
        if 'returns_mean' in analysis_results:
            detailed_metrics['Annual Return'] = f"{analysis_results['returns_mean']*100:.2f}%"
        if 'returns_std' in analysis_results:
            detailed_metrics['Annual Volatility'] = f"{analysis_results['returns_std']*100:.2f}%"
        if 'sharpe_ratio' in analysis_results:
            detailed_metrics['Sharpe Ratio'] = f"{analysis_results['sharpe_ratio']:.4f}"
        if 'sortino_ratio' in analysis_results:
            detailed_metrics['Sortino Ratio'] = f"{analysis_results['sortino_ratio']:.4f}"
        if 'var' in analysis_results:
            detailed_metrics['VaR (95%)'] = f"{analysis_results['var'].get(0.95, 0)*100:.2f}%"
            detailed_metrics['VaR (99%)'] = f"{analysis_results['var'].get(0.99, 0)*100:.2f}%"
        if 'cvar' in analysis_results:
            detailed_metrics['CVaR (95%)'] = f"{analysis_results['cvar'].get(0.95, 0)*100:.2f}%"
            detailed_metrics['CVaR (99%)'] = f"{analysis_results['cvar'].get(0.99, 0)*100:.2f}%"
        if 'max_drawdown' in analysis_results:
            detailed_metrics['Maximum Drawdown'] = f"{abs(analysis_results['max_drawdown'])*100:.2f}%"
        if 'beta' in analysis_results:
            detailed_metrics['Beta'] = f"{analysis_results['beta']:.4f}"
        if 'tracking_error' in analysis_results:
            detailed_metrics['Tracking Error'] = f"{analysis_results['tracking_error']*100:.2f}%"
        
        metrics_table = self.create_summary_table(detailed_metrics, "Risk Metrics")
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # Distribution analysis
        if 'distribution' in analysis_results:
            dist_heading = Paragraph("Return Distribution Analysis", self.heading_style)
            story.append(dist_heading)
            
            dist_metrics = {
                'Mean Daily Return': f"{analysis_results['distribution']['mean']*100:.4f}%",
                'Daily Volatility': f"{analysis_results['distribution']['std']*100:.4f}%",
                'Skewness': f"{analysis_results['distribution']['skewness']:.4f}",
                'Kurtosis': f"{analysis_results['distribution']['kurtosis']:.4f}",
                'Jarque-Bera Statistic': f"{analysis_results['distribution']['jarque_bera_stat']:.4f}",
                'Jarque-Bera P-Value': f"{analysis_results['distribution']['jarque_bera_pvalue']:.6f}"
            }
            
            dist_table = self.create_summary_table(dist_metrics, "Distribution Metrics")
            story.append(dist_table)
            story.append(Spacer(1, 20))
        
        # Risk interpretation
        interpretation_heading = Paragraph("Risk Interpretation", self.heading_style)
        story.append(interpretation_heading)
        
        interpretation_text = """
        <b>Value at Risk (VaR):</b> The maximum expected loss over a specific time period at a given confidence level.<br/><br/>
        <b>Conditional VaR (CVaR):</b> The expected loss given that VaR has been exceeded (tail risk).<br/><br/>
        <b>Sharpe Ratio:</b> Risk-adjusted return measure. Higher values indicate better risk-adjusted performance.<br/><br/>
        <b>Maximum Drawdown:</b> The largest peak-to-trough decline in portfolio value.<br/><br/>
        <b>Skewness:</b> Measure of return distribution asymmetry. Negative values indicate more extreme negative returns.<br/><br/>
        <b>Kurtosis:</b> Measure of tail heaviness. Higher values indicate more extreme outliers.
        """
        
        interpretation_para = Paragraph(interpretation_text, self.styles['Normal'])
        story.append(interpretation_para)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_portfolio_optimization_report(self, optimization_results: Dict,
                                             portfolio_data: Dict,
                                             portfolio_name: str = "Optimized Portfolio") -> bytes:
        """
        Generate portfolio optimization PDF report
        
        Args:
            optimization_results: Dictionary with optimization results
            portfolio_data: Portfolio composition and performance data
            portfolio_name: Name of the portfolio
            
        Returns:
            PDF bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Title
        title = Paragraph(f"Portfolio Optimization Report - {portfolio_name}", self.title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Report metadata
        report_date = datetime.now().strftime("%B %d, %Y at %H:%M")
        metadata = Paragraph(f"Generated on {report_date}", self.styles['Normal'])
        story.append(metadata)
        story.append(Spacer(1, 20))
        
        # Optimization summary
        summary_heading = Paragraph("Optimization Summary", self.heading_style)
        story.append(summary_heading)
        
        if 'max_sharpe' in optimization_results:
            max_sharpe = optimization_results['max_sharpe']
            summary_metrics = {
                'Expected Annual Return': f"{max_sharpe['expected_return']*100:.2f}%",
                'Annual Volatility': f"{max_sharpe['volatility']*100:.2f}%",
                'Sharpe Ratio': f"{max_sharpe['sharpe_ratio']:.4f}",
                'Optimization Success': "Yes" if max_sharpe['success'] else "No"
            }
            
            summary_table = self.create_summary_table(summary_metrics, "Optimal Portfolio Metrics")
            story.append(summary_table)
            story.append(Spacer(1, 20))
        
        # Portfolio composition
        composition_heading = Paragraph("Portfolio Composition", self.heading_style)
        story.append(composition_heading)
        
        if 'max_sharpe' in optimization_results and 'asset_names' in portfolio_data:
            weights = optimization_results['max_sharpe']['weights']
            asset_names = portfolio_data['asset_names']
            
            composition_data = [['Asset', 'Weight (%)']]
            for asset, weight in zip(asset_names, weights):
                if weight > 0.001:  # Only show significant weights
                    composition_data.append([asset, f"{weight*100:.2f}%"])
            
            composition_table = Table(composition_data, colWidths=[3*inch, 2*inch])
            composition_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            
            story.append(composition_table)
            story.append(Spacer(1, 20))
        
        # Risk analysis
        risk_heading = Paragraph("Risk Analysis", self.heading_style)
        story.append(risk_heading)
        
        if 'min_volatility' in optimization_results:
            min_vol = optimization_results['min_volatility']
            max_sharpe = optimization_results['max_sharpe']
            
            risk_comparison = {
                'Max Sharpe Return': f"{max_sharpe['expected_return']*100:.2f}%",
                'Max Sharpe Volatility': f"{max_sharpe['volatility']*100:.2f}%",
                'Min Volatility Return': f"{min_vol['expected_return']*100:.2f}%",
                'Min Volatility Risk': f"{min_vol['volatility']*100:.2f}%",
                'Risk Reduction': f"{((max_sharpe['volatility'] - min_vol['volatility'])/max_sharpe['volatility']*100):.1f}%"
            }
            
            risk_table = self.create_summary_table(risk_comparison, "Risk Comparison")
            story.append(risk_table)
            story.append(Spacer(1, 20))
        
        # Investment recommendations
        recommendations_heading = Paragraph("Investment Recommendations", self.heading_style)
        story.append(recommendations_heading)
        
        recommendations_text = """
        <b>Maximum Sharpe Ratio Portfolio:</b> Recommended for investors seeking optimal risk-adjusted returns. 
        This portfolio maximizes the excess return per unit of risk.<br/><br/>
        
        <b>Minimum Volatility Portfolio:</b> Suitable for conservative investors prioritizing capital preservation 
        with lower volatility tolerance.<br/><br/>
        
        <b>Diversification Benefits:</b> The optimized portfolio provides improved risk-adjusted returns through 
        strategic asset allocation based on Modern Portfolio Theory principles.<br/><br/>
        
        <b>Rebalancing:</b> Regular portfolio rebalancing is recommended to maintain optimal weights as market 
        conditions change.
        """
        
        recommendations_para = Paragraph(recommendations_text, self.styles['Normal'])
        story.append(recommendations_para)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_options_pricing_report(self, option_data: Dict, 
                                      option_type: str = "call") -> bytes:
        """
        Generate options pricing analysis PDF report
        
        Args:
            option_data: Dictionary with option pricing results
            option_type: Type of option ('call' or 'put')
            
        Returns:
            PDF bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Title
        title = Paragraph(f"Options Pricing Analysis - {option_type.capitalize()} Option", self.title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Report metadata
        report_date = datetime.now().strftime("%B %d, %Y at %H:%M")
        metadata = Paragraph(f"Generated on {report_date}", self.styles['Normal'])
        story.append(metadata)
        story.append(Spacer(1, 20))
        
        # Option specifications
        specs_heading = Paragraph("Option Specifications", self.heading_style)
        story.append(specs_heading)
        
        if 'parameters' in option_data:
            params = option_data['parameters']
            specs = {
                'Underlying Price': f"${params.get('spot_price', 0):.2f}",
                'Strike Price': f"${params.get('strike_price', 0):.2f}",
                'Time to Expiration': f"{params.get('time_to_expiry', 0):.4f} years",
                'Risk-Free Rate': f"{params.get('risk_free_rate', 0)*100:.2f}%",
                'Volatility': f"{params.get('volatility', 0)*100:.2f}%",
                'Option Type': option_type.capitalize()
            }
            
            specs_table = self.create_summary_table(specs, "Option Parameters")
            story.append(specs_table)
            story.append(Spacer(1, 20))
        
        # Pricing results
        pricing_heading = Paragraph("Pricing Results", self.heading_style)
        story.append(pricing_heading)
        
        if 'black_scholes_price' in option_data:
            pricing_results = {
                'Black-Scholes Price': f"${option_data['black_scholes_price']:.4f}",
                'Intrinsic Value': f"${option_data.get('intrinsic_value', 0):.4f}",
                'Time Value': f"${option_data.get('time_value', 0):.4f}",
                'Moneyness': option_data.get('moneyness', 'N/A')
            }
            
            pricing_table = self.create_summary_table(pricing_results, "Valuation")
            story.append(pricing_table)
            story.append(Spacer(1, 20))
        
        # Greeks analysis
        greeks_heading = Paragraph("Greeks Analysis", self.heading_style)
        story.append(greeks_heading)
        
        if 'greeks' in option_data:
            greeks = option_data['greeks']
            greeks_data = {
                'Delta': f"{greeks.get('delta', 0):.4f}",
                'Gamma': f"{greeks.get('gamma', 0):.4f}",
                'Theta': f"{greeks.get('theta', 0):.4f}",
                'Vega': f"{greeks.get('vega', 0):.4f}",
                'Rho': f"{greeks.get('rho', 0):.4f}"
            }
            
            greeks_table = self.create_summary_table(greeks_data, "Greeks")
            story.append(greeks_table)
            story.append(Spacer(1, 20))
        
        # Greeks interpretation
        interpretation_heading = Paragraph("Greeks Interpretation", self.heading_style)
        story.append(interpretation_heading)
        
        interpretation_text = """
        <b>Delta:</b> Price sensitivity to underlying asset price changes. Represents hedge ratio.<br/><br/>
        <b>Gamma:</b> Rate of change of delta. Higher gamma indicates delta changes more rapidly.<br/><br/>
        <b>Theta:</b> Time decay. Shows how much option value decreases per day, all else equal.<br/><br/>
        <b>Vega:</b> Sensitivity to volatility changes. Higher vega means more sensitive to volatility.<br/><br/>
        <b>Rho:</b> Sensitivity to interest rate changes. More relevant for longer-term options.
        """
        
        interpretation_para = Paragraph(interpretation_text, self.styles['Normal'])
        story.append(interpretation_para)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def export_data_to_csv(self, data: Dict[str, pd.DataFrame], filename_prefix: str = "financial_data") -> Dict[str, bytes]:
        """
        Export multiple datasets to CSV format
        
        Args:
            data: Dictionary with dataset names as keys and DataFrames as values
            filename_prefix: Prefix for filenames
            
        Returns:
            Dictionary with filenames as keys and CSV bytes as values
        """
        csv_files = {}
        
        for dataset_name, df in data.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                buffer = io.StringIO()
                df.to_csv(buffer, index=True)
                csv_content = buffer.getvalue().encode('utf-8')
                
                filename = f"{filename_prefix}_{dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                csv_files[filename] = csv_content
        
        return csv_files
