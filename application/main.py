# main.py
import d6tflow
from analysis_tasks import LoadDrawingTask, ProcessPixelDataTask, AnalyzeDrawingTask

# Set the image path
image_path = "path/to/drawing.png"

# Set the target task
d6tflow.set_dir("path/to/output/directory")
target_task = AnalyzeDrawingTask(image_path=image_path)

# Run the workflow
d6tflow.run(target_task)

# Load and print the results
result = target_task.outputLoad()
print(result)
