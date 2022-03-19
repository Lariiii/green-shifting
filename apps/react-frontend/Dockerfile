FROM cypress/base:16.13.0
WORKDIR /app
ENV PORTWOW=3000
COPY package*.json ./
RUN npm install
EXPOSE 3000
CMD ["npm","start"]
