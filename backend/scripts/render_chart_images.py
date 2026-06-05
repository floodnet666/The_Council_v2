import json
import plotly.graph_objects as go
import plotly.io as pio
import os

# Save images to artifacts directory so the walkthrough can embed them
OUT_DIR = r"C:\Users\thiag\.gemini\antigravity\brain\06d07e8b-fab3-4840-b69f-4545c00f01ef"

def render_charts():
    with open("designer_bench_1.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for q_type, item in data.items():
        config = item.get("visual_config")
        viz_data = item.get("visual_data")
        
        if not config or not viz_data:
            print(f"Skipping {q_type} - missing data/config")
            continue
            
        chart_type = config.get("chart_type")
        x_axis = config.get("x_axis")
        y_axis = config.get("y_axis")
        title = config.get("title", "Chart")
        
        fig = go.Figure()
        
        if chart_type == "pie":
            labels = [row[x_axis] for row in viz_data]
            values = [row[y_axis] for row in viz_data]
            fig.add_trace(go.Pie(labels=labels, values=values))
        else:
            x_vals = [row[x_axis] for row in viz_data]
            y_vals = [row[y_axis] for row in viz_data]
            
            if chart_type == "bar":
                fig.add_trace(go.Bar(x=x_vals, y=y_vals, marker_color="#06b6d4"))
            elif chart_type == "line":
                fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode="lines+markers", marker_color="#06b6d4"))
            elif chart_type == "scatter":
                fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode="markers", marker_color="#06b6d4"))
                
        fig.update_layout(
            title=title,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ededed")
        )
        
        out_path = os.path.join(OUT_DIR, f"chart_{q_type}.png")
        fig.write_image(out_path)
        print(f"Saved {out_path}")

if __name__ == "__main__":
    render_charts()
