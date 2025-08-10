"""
EDA Report generation utilities for the AI Data Assistant.
Handles automated exploratory data analysis report creation.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import tempfile
import base64
import os
import streamlit.components.v1 as components


class EDAReportGenerator:
    """Handles generation of comprehensive EDA reports."""

    def __init__(self, df):
        """
        Initialize EDA report generator.

        Args:
            df (pd.DataFrame): The dataframe to analyze
        """
        self.df = df
        self.numeric_cols = df.select_dtypes(include=["number"]).columns
        self.categorical_cols = df.select_dtypes(include=["object"]).columns

    def generate_automated_report(self):
        """Generate automated EDA report using ydata-profiling."""
        st.markdown(
            '<div class="section-header">📊 Automated EDA Report</div>',
            unsafe_allow_html=True,
        )

        try:
            from ydata_profiling import ProfileReport

            with st.spinner(
                "Generating comprehensive EDA report... This may take a moment."
            ):
                progress = st.progress(0)

                progress.progress(25)
                st.info("Analyzing data structure and statistics...")

                # Check dataset size and optimize accordingly
                df_for_analysis = self._prepare_dataset_for_analysis()

                try:
                    # Generate optimized profile
                    profile = self._create_optimized_profile(df_for_analysis)

                    progress.progress(75)
                    st.info("Creating visualizations and correlations...")

                    # Generate and display report
                    self._generate_and_display_report(profile, progress)

                except Exception as profile_error:
                    st.error(f"Error with profile generation: {profile_error}")
                    # Ultra-minimal fallback
                    self._generate_fallback_report()

        except ImportError:
            st.error(
                "ydata-profiling not installed. Please install it using: `pip install ydata-profiling`"
            )
            self._generate_manual_eda()

        except Exception as e:
            st.error(f"Error generating EDA report: {str(e)}")
            st.info("💡 Please try again or contact support if the issue persists.")

    def _prepare_dataset_for_analysis(self):
        """Prepare dataset for analysis, handling large datasets."""
        rows, cols = self.df.shape

        if rows > 10000 or cols > 50:
            st.warning(
                f"⚠️ Large dataset detected ({rows:,} rows, {cols} columns). Report generation may take longer and some features will be simplified."
            )

        # Sample large datasets
        if rows > 10000:
            df_for_analysis = self.df.sample(n=10000, random_state=42)
            st.info(
                f"Using sample of 10,000 rows for analysis (original: {rows:,} rows)"
            )
            return df_for_analysis

        return self.df

    def _create_optimized_profile(self, df):
        """Create optimized ProfileReport configuration."""
        from ydata_profiling import ProfileReport

        return ProfileReport(
            df,
            title="Data Analysis Report",
            minimal=True,  # Use minimal mode to reduce complexity
            explorative=False,  # Disable heavy explorative analysis
            # Disable problematic visualizations
            plot={
                "correlation": {"cram_matrix": False},
                "missing": {"heatmap": False, "dendrogram": False},
                "histogram": {"bins": 20, "max_bins": 50},
            },
            # Reduce sample size for large datasets
            samples={"head": 10, "tail": 10, "random": 10},
            # Disable correlation matrix for large datasets
            correlations={
                "auto": {"calculate": len(df.columns) < 20},  # Only if < 20 columns
                "pearson": {"calculate": False},
                "spearman": {"calculate": False},
                "kendall": {"calculate": False},
                "phi_k": {"calculate": False},
                "cramers": {"calculate": False},
            },
            # Disable interactions for performance
            interactions={"targets": []},
            # Set figure size explicitly
            html={"style": {"full_width": True}},
            # Reduce memory usage
            vars={"num": {"low_categorical_threshold": 0}},
        )

    def _generate_fallback_report(self):
        """Generate ultra-minimal fallback report."""
        from ydata_profiling import ProfileReport

        profile = ProfileReport(
            self.df.head(500),
            title="Simplified Data Report",
            minimal=True,
            plot=False,
            correlations=False,
            missing_diagrams=False,
            interactions=False,
        )
        return profile

    def _generate_and_display_report(self, profile, progress):
        """Generate HTML report and display options."""
        # Generate HTML report
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            profile.to_file(f.name)

            progress.progress(90)

            # Read the HTML content
            with open(f.name, "r", encoding="utf-8") as file:
                html_content = file.read()

            progress.progress(100)
            progress.empty()

            st.success("✅ EDA Report generated successfully!")

            # Display control options
            self._display_report_controls(html_content)

            # Cleanup temp file
            os.unlink(f.name)

    def _display_report_controls(self, html_content):
        """Display report viewing and download controls."""
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            # Download button
            b64 = base64.b64encode(html_content.encode()).decode()
            href = f'<a href="data:text/html;base64,{b64}" download="eda_report.html" style="display: inline-block; padding: 0.5rem 1rem; background: linear-gradient(135deg, #16A34A, #0D9488); color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">📥 Download Report</a>'
            st.markdown(href, unsafe_allow_html=True)

        with col2:
            if st.button("View Report", use_container_width=True):
                st.session_state.show_embedded = True

        with col3:
            if st.button("Report Summary", use_container_width=True):
                st.session_state.show_summary = True

        # Show embedded report
        if st.session_state.get("show_embedded", False):
            self._show_embedded_report(html_content)

        # Show summary
        if st.session_state.get("show_summary", False):
            self._show_report_summary()

    def _show_embedded_report(self, html_content):
        """Display embedded HTML report."""
        st.markdown("---")
        st.markdown("### EDA Report Preview")
        st.info("💡 For best experience, download the report to view in full screen")

        # Close button
        if st.button("Close Report", key="close_report"):
            st.session_state.show_embedded = False
            st.rerun()

        components.html(html_content, height=600, scrolling=True)

    def _show_report_summary(self):
        """Display report summary statistics."""
        st.markdown("---")
        st.markdown("### Report Summary")

        # Close summary button
        if st.button("Close Summary", key="close_summary"):
            st.session_state.show_summary = False
            st.rerun()

        # Quick stats from the data
        missing_data = self.df.isnull().sum().sum()
        duplicates = self.df.duplicated().sum()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Numeric Variables", len(self.numeric_cols))
        with col2:
            st.metric("Categorical Variables", len(self.categorical_cols))
        with col3:
            st.metric("Missing Values", missing_data)
        with col4:
            st.metric("Duplicate Rows", duplicates)

        # Data quality insights
        st.markdown("**🔍 Key Insights:**")
        insights = self._generate_insights(missing_data, duplicates)

        for insight in insights:
            st.write(f"• {insight}")

    def _generate_insights(self, missing_data, duplicates):
        """Generate data quality insights."""
        insights = []

        if missing_data == 0:
            insights.append("✅ No missing values found")
        elif missing_data > 0:
            insights.append(f"⚠️ {missing_data} missing values detected")

        if duplicates == 0:
            insights.append("✅ No duplicate rows found")
        elif duplicates > 0:
            insights.append(f"⚠️ {duplicates} duplicate rows detected")

        if len(self.numeric_cols) > 1:
            insights.append(
                "📊 Multiple numeric variables available for correlation analysis"
            )

        if len(self.categorical_cols) > 0:
            insights.append("Categorical variables available for grouping analysis")

        return insights

    def _generate_manual_eda(self):
        """Generate manual EDA as fallback."""
        st.info("💡 Showing manual EDA instead...")
        st.markdown("### 📊 Basic Data Analysis")

        # Basic statistics
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Numeric Variables Summary**")
            numeric_data = self.df.select_dtypes(include=["number"])
            if not numeric_data.empty:
                st.dataframe(numeric_data.describe())
            else:
                st.write("No numeric variables found")

        with col2:
            st.markdown("**📋 Dataset Information**")
            info_data = {
                "Metric": [
                    "Total Rows",
                    "Total Columns",
                    "Memory Usage (MB)",
                    "Missing Values",
                    "Duplicate Rows",
                ],
                "Value": [
                    f"{len(self.df):,}",
                    len(self.df.columns),
                    f"{self.df.memory_usage(deep=True).sum() / 1024**2:.2f}",
                    self.df.isnull().sum().sum(),
                    self.df.duplicated().sum(),
                ],
            }
            st.dataframe(pd.DataFrame(info_data), hide_index=True)

        # Missing values chart if any exist
        missing_data = self.df.isnull().sum()
        if missing_data.sum() > 0:
            st.markdown("**🔍 Missing Values by Column**")
            fig = px.bar(
                x=missing_data.index,
                y=missing_data.values,
                title="Missing Values Count",
                labels={"x": "Columns", "y": "Missing Count"},
                color_discrete_sequence=["#2563EB"],
            )
            st.plotly_chart(fig, use_container_width=True)


def generate_eda_report(df):
    """
    Main function to generate EDA report.

    Args:
        df (pd.DataFrame): DataFrame to analyze
    """
    generator = EDAReportGenerator(df)
    generator.generate_automated_report()
