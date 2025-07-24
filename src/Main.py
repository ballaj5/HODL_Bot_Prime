import asyncio
import subprocess

# Assuming scheduler_main is an async function in this module
# from scheduler.retrain_scheduler import main as scheduler_main

async def run_pipeline():
    """Executes the pipeline shell script asynchronously."""
    print("Starting pipeline execution...")
    process = await asyncio.create_subprocess_shell(
        './run_pipeline.sh',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if process.returncode == 0:
        print("Pipeline executed successfully.")
        if stdout:
            print(f"[Pipeline STDOUT]:\n{stdout.decode()}")
    else:
        print(f"Pipeline execution failed with return code {process.returncode}.")
        if stderr:
            print(f"[Pipeline STDERR]:\n{stderr.decode()}")


async def main():
    """
    Runs the main application tasks concurrently.
    NOTE: `scheduler_main` is commented out as the file was not provided.
          Uncomment it when you have the scheduler ready.
    """
    tasks = [
        run_pipeline()
        # scheduler_main() # Uncomment when scheduler is implemented
    ]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # In a real scenario, you might want to run this on a loop
    # or triggered by an external event.
    asyncio.run(main())