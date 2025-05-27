# Dynamic Property Performance Executive Summary (Power BI)

## 📊 Project Overview

This project delivers an interactive and intelligent Power BI dashboard designed to provide a dynamic executive summary of property performance. Leveraging advanced DAX measures, the report automatically generates a narrative analysis and actionable recommendations, adapting in real-time to user-selected filters (e.g., year, country, property type, or individual property ID). This eliminates the need for manual report generation, empowering stakeholders with immediate, context-aware insights.

## 🎯 Objectives

* To develop a **highly dynamic and interactive Power BI report** that provides an executive-level overview of property performance.
* To implement **advanced DAX measures** capable of generating human-readable narrative summaries and key recommendations based on selected data context.
* To enable **self-service analytics** for stakeholders, allowing them to instantly drill down into specific segments (e.g., a single property) and receive tailored insights.
* To demonstrate expertise in **data modeling, DAX formula authoring, and sophisticated Power BI report design** for executive decision-making.

## 🛠️ Tools & Technologies Used

* **Power BI Desktop:** For data modeling, DAX measure creation, report design, and visualization.
* **MySQL:** For storing and managing the raw property and booking data.
* **Python:** Used for data generation, cleaning, or transformation scripts. Libraries used `Pandas`, `Faker`, `NumPy`).
* **DAX (Data Analysis Expressions):** The core language used for creating all dynamic measures, enabling complex calculations and conditional text generation.

## 💾 Dataset Generation & Structure

The dataset underpinning this report was synthetically generated (using a Python script in VS Code). It is designed to simulate realistic property booking, revenue, and review data.

### Data Sources:
* **`Bookings`:** Contains transactional data for property bookings, including dates, revenue, and links to properties.
* **`Property`:** Stores static information about each property, such as ID, type, country, and potentially owner.
* **`Calendar`:** A standard date dimension table for time-based filtering and analysis.
* **`Reviews`:** Detailed guest review data, including ratings.
* **`Owner`:** (If applicable) Information about property owners.

### Key Fields & Relationships:
The data model is structured with a star schema approach to optimize performance and analytical capabilities. Key relationships include:
* `Bookings` [Property ID] to `dim_property` [Property ID]
* `Bookings` [Date] to `dim_date` [Date]
* `Reviews` [Property ID] to `dim_property` [Property ID]

## 💡 Key Insights & Analytical Capabilities

This report is designed to provide actionable insights at both a **portfolio level** and a **single property level**. Users can intuitively interact with slicers to filter data by:

* **Time Period:** Analyze performance trends over specific years or date ranges.
* **Geographic Location:** Compare property performance across different countries.
* **Property Type:** Evaluate how different property categories (e.g., Resort, Apartment) are performing.
* **Individual Property:** Drill down into the granular details and receive a personalized summary for a single property.

### The report's dynamic summary provides:

* **Contextual Overview:** A clear statement of the current filters applied (e.g., "Performance for 2023 in USA for Resorts").
* **Performance Snapshot:** Key metrics such as Total Revenue, Average Daily Rate (ADR), Occupancy Rate, and Average Rating, presented with comparisons against the overall portfolio average.
    * **Example Analysis:** "Property ID 20 generated $25,923 in Total Revenue. Its Average Daily Rate (ADR) of $370.33 is **above** the portfolio average of $246.71, indicating strong pricing."
* **Actionable Recommendations:** Intelligent, context-aware suggestions for improvement or areas to maintain strong performance. These recommendations adapt based on whether a single property or a portfolio segment is being viewed, and whether metrics are above or below benchmarks.
    * **Example Recommendation:** "Focus on Occupancy Improvement: The occupancy rate is below the portfolio average. Explore targeted promotions or refine booking platform strategies to increase utilization."

## 📈 Power BI Features Demonstrated

* **Advanced DAX:** Extensive use of `VAR`, `IF`, `HASONEVALUE`, `SELECTEDVALUE`, `UNICHAR(10)`, and complex string concatenation for dynamic narrative generation.
* **Measure Tables:** Organized DAX measures in a dedicated table for clarity and navigability.
* **Filter Context Management:** Effective use of `CALCULATE` with `ALL` and `ALLSELECTED` to manage context for accurate portfolio comparisons.
* **Interactive Visualizations:** Utilizing slicers and text box visuals for a highly interactive user experience.

## 🚀 How to Explore This Project

To fully interact with the dashboard and examine the underlying DAX and data model:

1.  **Clone or Download** this GitHub repository to your local machine.
2.  **Open the `.pbix` file** in Power BI Desktop.
3.  Navigate to the "Executive Summary" page.
4.  **Interact with the slicers** on other report pages (e.g., Year, Country, Property Type, Property ID) to observe the dynamic text updates in the Executive Summary.
5.  Explore the DAX measures in the "Dynamic Insight Queries" table to understand the logic behind the narrative generation.
6.  (Optional) If applicable, examine the Python/SQL scripts in the `/data` or `/scripts` folder for data generation/transformation details.
---
