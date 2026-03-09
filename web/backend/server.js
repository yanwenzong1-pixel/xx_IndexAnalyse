const http = require('http');

const PORT = 8080;

const server = http.createServer((req, res) => {
  res.statusCode = 200;
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');
  
  if (req.url === '/api/data' && req.method === 'GET') {
    res.end(JSON.stringify({
      success: true,
      data: {
        latest: {
          date: "2024-03-06",
          close: 1500.0,
          change_pct: 2.5,
          amount: 1000000000,
          turnover: 5.2
        },
        history: [
          {
            date: "2024-03-05",
            close: 1463.5,
            change_pct: -1.2,
            amount: 950000000,
            turnover: 4.8
          },
          {
            date: "2024-03-04",
            close: 1481.3,
            change_pct: 0.5,
            amount: 980000000,
            turnover: 5.0
          }
        ]
      }
    }));
  } else if (req.url === '/api/risk' && req.method === 'GET') {
    res.end(JSON.stringify({
      success: true,
      data: {
        risk_level: 5,
        downside_probability: 0.4,
        alert: false,
        alert_message: ""
      }
    }));
  } else if (req.url === '/api/refresh' && req.method === 'POST') {
    res.end(JSON.stringify({ success: true, message: "数据刷新成功" }));
  } else {
    res.end(JSON.stringify({ success: false, message: "API路径不存在" }));
  }
});

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
