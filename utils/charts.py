"""
Chart generation utilities for the AI Data Assistant.
Handles creation of various data visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class ChartGenerator:
    """Handles generation of various chart types for data visualization."""

    def __init__(self, df):
        """
        Initialize chart generator with dataframe.

        Args:
            df (pd.DataFrame): The dataframe to visualize
        """
        self.df = df
        self.numeric_cols = df.select_dtypes(include=["number"]).columns
        self.categorical_cols = df.select_dtypes(include=["object"]).columns

        # Professional color palette
        self.colors = {
            "primary": "#2563EB",
            "secondary": "#0D9488",
            "warning": "#F59E0B",
            "success": "#16A34A",
            "error": "#DC2626",
        }

    def generate_quick_visualizations(self):
        """Generate a set of quick visualizations based on data types."""
        st.markdown(
            '<div class="section-header">📈 Quick Visualizations</div>',
            unsafe_allow_html=True,
        )

        if len(self.numeric_cols) > 0:
            col1, col2 = st.columns(2)

            with col1:
                self._create_distribution_plot()

            with col2:
                if len(self.numeric_cols) > 1:
                    self._create_scatter_plot()
                else:
                    self._create_box_plot()

        if len(self.categorical_cols) > 0:
            self._create_categorical_plot()

    def _create_distribution_plot(self):
        """Create distribution plot for first numeric column."""
        if len(self.numeric_cols) == 0:
            return

        col = self.numeric_cols[0]
        fig = px.histogram(
            self.df,
            x=col,
            title=f"Distribution of {col}",
            color_discrete_sequence=[self.colors["primary"]],
            template="plotly_white",
        )

        fig.update_layout(
            title_font_size=16,
            title_x=0.5,
            showlegend=False,
            margin=dict(t=50, b=50, l=50, r=50),
        )

        st.plotly_chart(fig, use_container_width=True)

    def _create_scatter_plot(self):
        """Create scatter plot for first two numeric columns."""
        if len(self.numeric_cols) < 2:
            return

        x_col, y_col = self.numeric_cols[0], self.numeric_cols[1]
        fig = px.scatter(
            self.df,
            x=x_col,
            y=y_col,
            title=f"{x_col} vs {y_col}",
            color_discrete_sequence=[self.colors["secondary"]],
            template="plotly_white",
        )

        fig.update_layout(
            title_font_size=16,
            title_x=0.5,
            showlegend=False,
            margin=dict(t=50, b=50, l=50, r=50),
        )

        st.plotly_chart(fig, use_container_width=True)

    def _create_box_plot(self):
        """Create box plot for first numeric column."""
        if len(self.numeric_cols) == 0:
            return

        col = self.numeric_cols[0]
        fig = px.box(
            self.df,
            y=col,
            title=f"Box Plot of {col}",
            color_discrete_sequence=[self.colors["secondary"]],
            template="plotly_white",
        )

        fig.update_layout(
            title_font_size=16,
            title_x=0.5,
            showlegend=False,
            margin=dict(t=50, b=50, l=50, r=50),
        )

        st.plotly_chart(fig, use_container_width=True)

    def _create_categorical_plot(self):
        """Create bar chart for first categorical column."""
        if len(self.categorical_cols) == 0:
            return

        col = self.categorical_cols[0]
        value_counts = self.df[col].value_counts().head(10)

        fig = px.bar(
            x=value_counts.index,
            y=value_counts.values,
            title=f"Top 10 Values in {col}",
            labels={"x": col, "y": "Count"},
            color_discrete_sequence=[self.colors["warning"]],
            template="plotly_white",
        )

        fig.update_layout(
            title_font_size=16,
            title_x=0.5,
            showlegend=False,
            margin=dict(t=50, b=50, l=50, r=50),
            xaxis_tickangle=-45,
        )

        st.plotly_chart(fig, use_container_width=True)

    def create_correlation_heatmap(self):
        """Create correlation heatmap for numeric columns."""
        if len(self.numeric_cols) < 2:
            st.info("Need at least 2 numeric columns for correlation analysis.")
            return

        corr_matrix = self.df[self.numeric_cols].corr()

        fig = px.imshow(
            corr_matrix,
            title="Correlation Heatmap",
            color_continuous_scale="RdBu_r",
            aspect="auto",
            template="plotly_white",
        )

        fig.update_layout(
            title_font_size=16, title_x=0.5, margin=dict(t=50, b=50, l=50, r=50)
        )

        st.plotly_chart(fig, use_container_width=True)

    def create_missing_values_chart(self):
        """Create chart showing missing values by column."""
        missing_data = self.df.isnull().sum()
        missing_data = missing_data[missing_data > 0]

        if len(missing_data) == 0:
            st.success("✅ No missing values found in the dataset!")
            return

        fig = px.bar(
            x=missing_data.index,
            y=missing_data.values,
            title="Missing Values by Column",
            labels={"x": "Columns", "y": "Missing Count"},
            color_discrete_sequence=[self.colors["error"]],
            template="plotly_white",
        )

        fig.update_layout(
            title_font_size=16,
            title_x=0.5,
            showlegend=False,
            margin=dict(t=50, b=50, l=50, r=50),
            xaxis_tickangle=-45,
        )

        st.plotly_chart(fig, use_container_width=True)

    def create_data_types_chart(self):
        """Create pie chart showing distribution of data types."""
        type_counts = self.df.dtypes.value_counts()

        # Convert numpy dtypes to strings to make them JSON serializable
        type_names = [str(dtype) for dtype in type_counts.index]
        type_values = type_counts.values.tolist()  # Convert to list

        fig = px.pie(
            values=type_values,
            names=type_names,
            title="Distribution of Data Types",
            color_discrete_sequence=px.colors.qualitative.Set3,
            template="plotly_white",
        )

        fig.update_layout(
            title_font_size=16, title_x=0.5, margin=dict(t=50, b=50, l=50, r=50)
        )

        st.plotly_chart(fig, use_container_width=True)


def create_stats_visualization(df):
    """
    Create statistical visualization widgets.

    Args:
        df (pd.DataFrame): The dataframe to visualize
    """
    chart_gen = ChartGenerator(df)

    # Create tabs for different chart types
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Quick Charts", "🔗 Correlations", "❓ Missing Data", "📋 Data Types"]
    )

    with tab1:
        chart_gen.generate_quick_visualizations()

    with tab2:
        chart_gen.create_correlation_heatmap()

    with tab3:
        chart_gen.create_missing_values_chart()

    with tab4:
        chart_gen.create_data_types_chart()
