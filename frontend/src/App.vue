<template>
  <div id="app">
    <header class="app-header">
      <h1>🏃 我的健康数据分析平台</h1>
      <p>前后端分离版本 - 升级版</p>
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
          <button @click="exportCSV" class="btn-secondary">📥 导出 CSV</button>
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

        <!-- Plotly 图表 -->
        <div v-if="records.length" class="charts-section">
          <h3>📈 数据可视化</h3>
          <plotly :data="plotlyData" :layout="plotlyLayout" :options="{responsive:true}" style="width:100%;height:500px;"></plotly>
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
            <!-- AI 小结 -->
            <button @click="generateAISummary(record.id)" class="btn-secondary btn-small">🤖 生成 AI 小结</button>
            <div v-if="aiSummaries[record.id]" class="ai-summary">
              <strong>AI 小结:</strong>
              <ul>
                <li v-for="obs in aiSummaries[record.id].observations" :key="obs">{{ obs }}</li>
                <li v-for="sug in aiSummaries[record.id].suggestions" :key="sug"><em>{{ sug }}</em></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Plotly from 'vue-plotly';

const API_BASE = 'http://localhost:5000/api';

export default {
  name: 'App',
  components: { plotly: Plotly },
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
      analysis: null,
      aiSummaries: {},
      plotlyData: [],
      plotlyLayout: {}
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
        this.preparePlotlyData();
      } catch (error) {
        console.error('加载数据失败:', error);
      }
    },

    async addRecord() {
      try {
        await axios.post(`${API_BASE}/health/records`, this.newRecord);
        await this.loadRecords();
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
    },

    async generateAISummary(recordId) {
      try {
        const response = await axios.get(`${API_BASE}/health/analysis/per_run`);
        const summary = response.data.find(item => item.id === recordId);
        if (summary) {
          this.$set(this.aiSummaries, recordId, summary.summary);
        }
      } catch (error) {
        console.error('生成 AI 小结失败:', error);
      }
    },

    preparePlotlyData() {
      if (!this.records.length) return;
      const dates = this.records.map(r => r.日期);
      const durations = this.records.map(r => r.运动时长);
      const sleepHours = this.records.map(r => r.睡眠时长);

      this.plotlyData = [
        { x: dates, y: durations, type: 'scatter', mode: 'lines+markers', name: '运动时长(分钟)' },
        { x: dates, y: sleepHours, type: 'scatter', mode: 'lines+markers', name: '睡眠时长(小时)' }
      ];
      this.plotlyLayout = {
        title: '运动与睡眠趋势',
        xaxis: { title: '日期' },
        yaxis: { title: '时长' },
        legend: { orientation: 'h' }
      };
    },

    exportCSV() {
      if (!this.records.length) return;
      const csvContent = [
        Object.keys(this.records[0]).join(','),
        ...this.records.map(r => Object.values(r).join(','))
      ].join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', 'fitness_records.csv');
      link.click();
    }
  }
}
</script>

<style>
/* 原有样式不变，可复用前一个 App.vue 的样式 */
.btn-small {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
  margin-top: 0.5rem;
}
.ai-summary {
  background: #f1f8e9;
  padding: 0.75rem;
  margin-top: 0.5rem;
  border-radius: 6px;
}
</style>
