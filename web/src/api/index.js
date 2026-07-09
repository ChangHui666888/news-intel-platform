import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

export default {
  getNews(params)          { return api.get('/news', { params }) },
  getNewsById(id)          { return api.get(`/news/${id}`) },
  getHot(limit=10)         { return api.get('/news/hot', { params: { limit } }) },
  getLatest(limit=20)      { return api.get('/news/latest', { params: { limit } }) },
  search(q, page=1)        { return api.get(`/news/search?q=${q}&page=${page}`) },
  getCategories()          { return api.get('/categories') },
  getTags()                { return api.get('/tags') },
  login(email, password)   { return api.post('/login', { email, password }) },
  subscribe(tag)           { return api.post('/subscribe', { tag }) },
}
