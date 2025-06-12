import plotly.graph_objects as go
from typing import List, Dict, Tuple


class ChartService:
    """Service class for generating chart data."""
    
    @staticmethod
    def generate_heart_rate_chart(heart_rate_data: List[Dict]) -> go.Figure:
        """Generate Plotly heart rate chart data."""
        patients = [data["patient_name"] for data in heart_rate_data]
        moderate_values = [data["moderate"] for data in heart_rate_data]
        intense_values = [data["intense"] for data in heart_rate_data]
        
        fig = go.Figure()
        
        # Add moderate bars with consistent width (Plotly default colors)
        fig.add_trace(go.Bar(
            name='Moderate',
            x=patients,
            y=moderate_values,
            width=0.35,  # Fixed width for consistency
            offsetgroup=1,  # Group bars together
            hovertemplate='<b>%{x}</b><br>Moderate: %{y} bpm<extra></extra>'
        ))
        
        # Add intense bars with same width (Plotly default colors)
        fig.add_trace(go.Bar(
            name='Intense',
            x=patients,
            y=intense_values,
            width=0.35,  # Same fixed width
            offsetgroup=2,  # Group bars together
            hovertemplate='<b>%{x}</b><br>Intense: %{y} bpm<extra></extra>'
        ))
        
        # Update layout with proper margins and remove Plotly logo
        fig.update_layout(
            title=dict(
                text="Heart Rate Monitoring",
                font=dict(size=18, family="Inter, sans-serif", color="#111827"),
                x=0.05,  # Move title slightly right
                y=0.95   # Move title down to give more space
            ),
            xaxis_title="Patients",
            yaxis_title="Heart Rate (bpm)",
            barmode='group',
            bargap=0.6,  # Gap between groups of bars
            bargroupgap=0.5,  # Gap between bars in the same group
            height=380,
            # CRITICAL: Proper margins to avoid border issues
            margin=dict(l=60, r=30, t=50, b=50, pad=10),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", color="#374151"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1
            ),
            hovermode='x unified'
        )
        
        # Style axes with proper spacing
        fig.update_xaxes(
            showgrid=False,
            showline=True,
            linewidth=1,
            linecolor='#E5E7EB',
            tickfont=dict(size=11),
            title_font=dict(size=12),
            title_standoff=20  # Space between axis and title
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='#F3F4F6',
            showline=True,
            linewidth=1,
            linecolor='#E5E7EB',
            tickfont=dict(size=11),
            title_font=dict(size=12),
            title_standoff=30  # Space between axis and title
        )
        
        return fig

    @staticmethod
    def generate_age_distribution_chart(age_distribution: List[Tuple[str, int]]) -> go.Figure:
        """Generate Plotly age distribution chart data."""
        if not age_distribution:
            # Default data if no distribution available
            labels = ['18-25', '26-35', '36-45', '46-55', '55+']
            values = [8, 10, 12, 8, 3]
        else:
            labels = [item[0] for item in age_distribution]
            values = [item[1] for item in age_distribution]
        
        # Use Plotly's default color palette (remove explicit colors)
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.6,
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(size=11, family="Inter, sans-serif"),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
            pull=[0.02, 0.02, 0.02, 0.02, 0.02]  # Slight separation for visual appeal
        )])
        
        fig.update_layout(
            title=dict(
                text="Age Group Distribution",
                font=dict(size=18, family="Inter, sans-serif", color="#111827"),
                x=0.5,
                y=0.95,
                xanchor='center'
            ),
            height=380,
            # CRITICAL: Proper margins to avoid border clipping
            margin=dict(l=40, r=40, t=50, b=60, pad=10),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", color="#374151"),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1,
                font=dict(size=10)
            )
        )
        
        # Add center annotation with better positioning
        fig.add_annotation(
            text=f"<b>{sum(values)}</b><br><span style='font-size:12px'>Total</span><br><span style='font-size:12px'>Patients</span>",
            x=0.5, y=0.5,
            font_size=14,
            font_color="#111827",
            showarrow=False,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1
        )
        
        return fig 