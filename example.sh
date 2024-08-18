# Install 
python -m venv venv 
source venv/bin/activate
pip install -r requirements.txt


# Add OPENAI_API_KEY to your environment variables
echo "OPENAI_API_KEY='YOUR_OPENAI_API_KEY'" > .env
source .env

# Run 
python image_roaster.py
python image_roaster.py path/to/your/image.jpg

