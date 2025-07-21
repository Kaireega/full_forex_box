import axios from "axios";

axios.defaults.baseURL =  process.env.REACT_APP_API_URL;

const response = (resp) => resp.data;

const requests = {
    get: (url) => axios.get(url).then(response)
}

const endPoints = {
    account: () => requests.get("/account"),
    headlines: () => requests.get("/headlines"),
    options: () => requests.get("/options"),
    technicals: (p,g) => requests.get(`/technicals/${p}/${g}`),
    prices: (p,g,c) => requests.get(`/prices/${p}/${g}/${c}`),
    te_calendar:(s,e) => requests.get(`/te/calendar/${s}/${e}`),
    ff_calendar:(s) => requests.get(`/ff/calendar/${s}`)


}

export default endPoints;