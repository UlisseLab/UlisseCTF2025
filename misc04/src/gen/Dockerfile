FROM node:22.9

WORKDIR /app

RUN apt update && apt-get install -y libcairo2-dev libpango1.0-dev

COPY main.js main.js
COPY Helvetica-Bold.ttf Helvetica-Bold.ttf

RUN npm install canvas dotenv tqdm

CMD ["node"]
