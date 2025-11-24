<template>
  <div id="app">
    <header class="app-header">
      <h1>🏃 我的健康数据分析平台</h1>
      <p>前后端分离版本 - 由我自己开发</p>
    </header>

    <div class="container">
      <!-- 数据输入 -->
      <div class="input-section">
        <h2>📝 添加健康记录</h2>
        <div class="input-form">
          <input v-model="newRecord.日期" placeholder="日期 (YYYY-MM-DD)" type="date">
          <input v-model="newRecord.运动项目" placeholder="运动项目">
          <input v-model="newRecord.运动时长" placeholder="运动时长(分钟)" type="number">
          <input v-model="newRecord.睡眠时长" placeholder="睡眠时长(小时)" type="number" step="0.1">
          <input v-model="newRecord.睡眠质量" placeholder="睡眠质量(1-5)" type="number" min="1" max="5">
          <textarea v-model="newRecord.心路历程" placeholder="心路历程..."></textarea>
          
          <button @click="addRecord" class="btn-primary">💾 保存记录</button>
        </div>
      </div>

      <!-- 分析功能 -->
      <div class="analysis-section">
        <h2>🤖 智能健康分析</h2>
        <div class="analysis-buttons">
          <button @click="getHealthTip" class="btn-secondary">💡 获取健康小贴士</button>
          <button @click="getAnalysis" class="btn-secondary">🔍 生成健康报告</button>
        </div>
        
        <div v-if="currentTip" class="tip-card">
          <strong>今日小贴士：</strong> {{ currentTip }}
        </div>

        <div v-if="analysis" class="analysis-result">
          <h3>📊 分析报告</h3>
          <div class="analysis-grid">
            <div class="analysis-card">
              <h4>🏃 运动分析</h4>
              <p>{{ analysis.sport_analysis }}</p>
              <div class="stats">
                <span>平均时长: {{ analysis.stats.avg_duration }}分钟</span>
                <span>运动天数: {{ analysis.stats.active_days }}</span>
                <span>运动种类: {{ analysis.stats.sport_variety }}</span>
              </div>
            </div>
            
            <div class="analysis-card">
              <h4>😴 睡眠分析</h4>
              <p>{{ analysis.sleep_analysis }}</p>
              <div class="stats">
                <span>平均睡眠: {{ analysis.stats.avg_sleep }}小时</span>
                <span>总记录: {{ analysis.stats.total_records }}条</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据展示 -->
      <div class="data-section">
        <h2>📋 所有记录 ({{ records.length }}条)</h2>
        <div class="records-list">
          <div v-for="record in records" :key="record.id" class="record-card">
            <div class="record-header">
              <strong>{{ record.日期 }}</strong>
              <span class="sport-type">{{ record.运动项目 }}</span>
            </div>
            <div class="record-details">
              <span>运动: {{ record.运动时长 }}分钟</span>
              <span>睡眠: {{ record.睡眠时长 }}小时</span>
              <span v-if="record.睡眠质量">质量: {{ record.睡眠质量 }}/5</span>
            </div>
            <div v-if="record.心路历程" class="record-notes">
              {{ record.心路历程 }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

export default {
  name: 'App',
  data() {
    return {
      records: [],
      newRecord: {
        日期: new Date().toISOString().split('T')[0],
        运动项目: '',
        运动时长: '',
        睡眠时长: '',
        睡眠质量: '',
        心路历程: ''
      },
      currentTip: '',
      analysis: null
    }
  },
  async mounted() {
    await this.loadRecords();
  },
  methods: {
    async loadRecords() {
      try {
        const response = await axios.get(`${API_BASE}/health/records`);
        this.records = response.data.data;
      } catch (error) {
        console.error('加载数据失败:', error);
      }
    },
    
    async addRecord() {
      try {
        await axios.post(`${API_BASE}/health/records`, this.newRecord);
        await this.loadRecords();
        
        // 清空表单
        this.newRecord = {
          日期: new Date().toISOString().split('T')[0],
          运动项目: '',
          运动时长: '',
          睡眠时长: '',
          睡眠质量: '',
          心路历程: ''
        };
        
        alert('记录添加成功！');
      } catch (error) {
        console.error('添加记录失败:', error);
        alert('添加失败，请检查数据格式');
      }
    },
    
    async getHealthTip() {
      try {
        const response = await axios.get(`${API_BASE}/health/tips`);
        this.currentTip = response.data.tip;
      } catch (error) {
        console.error('获取小贴士失败:', error);
      }
    },
    
    async getAnalysis() {
      try {
        const response = await axios.get(`${API_BASE}/health/analysis`);
        this.analysis = response.data;
      } catch (error) {
        console.error('获取分析失败:', error);
      }
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}

.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 2rem;
  text-align: center;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  color: #333;
  margin-bottom: 0.5rem;
}

.app-header p {
  color: #666;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.input-section, .analysis-section, .data-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.input-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 1rem;
}

.input-form input, .input-form textarea {
  padding: 0.75rem;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.input-form input:focus, .input-form textarea:focus {
  outline: none;
  border-color: #667eea;
}

.input-form textarea {
  grid-column: 1 / -1;
  min-height: 80px;
  resize: vertical;
}

.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  grid-column: 1 / -1;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5a6fd8;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #f8f9fa;
  color: #333;
  border: 2px solid #e1e5e9;
}

.btn-secondary:hover {
  background: #e9ecef;
  transform: translateY(-2px);
}

.analysis-buttons {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.tip-card {
  background: #e3f2fd;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
}

.analysis-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-top: 1rem;
}

.analysis-card {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.analysis-card h4 {
  margin-bottom: 0.5rem;
  color: #333;
}

.stats {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stats span {
  background: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

.records-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.record-card {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e1e5e9;
}

.record-header {
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 1rem;
}

.sport-type {
  background: #667eea;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.record-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.record-notes {
  background: white;
  padding: 0.75rem;
  border-radius: 4px;
  font-style: italic;
  color: #666;
}

@media (max-width: 768px) {
  .input-form {
    grid-template-columns: 1fr;
  }
  
  .analysis-grid {
    grid-template-columns: 1fr;
  }
  
  .records-list {
    grid-template-columns: 1fr;
  }
  
  .analysis-buttons {
    flex-direction: column;
  }
}
</style>
