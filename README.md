cd related-tickets
docker built -t related-tickets .
docker volume create related-tickets-assets
docker run -p 5000:5000 -v related-tickets-assets:/app/assets related-tickets --help
