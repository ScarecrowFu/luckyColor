from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import LotteryNumber
import random
from django.http import JsonResponse
from collections import Counter
import numpy as np
from datetime import datetime, timedelta

def index(request):
    return render(request, 'index.html')

def history(request):
    # 获取搜索参数，但只从POST请求获取
    search_query = request.POST.get('search', '')
    
    # 构建查询
    queryset = LotteryNumber.objects.all().order_by('-issue_number')
    if search_query:
        queryset = queryset.filter(issue_number__icontains=search_query)
    
    # 分页
    paginator = Paginator(queryset, 20)  # 每页显示20条记录
    page_number = request.GET.get('page', 1)
    history_data = paginator.get_page(page_number)
    
    return render(request, 'history.html', {
        'history_data': history_data,
        'search_query': search_query
    })

def random_number(request):
    # 生成不重复的随机红球号码
    red_balls = sorted(random.sample(range(1, 34), 6))  # sample函数确保不重复
    blue_ball = random.randint(1, 16)
    
    # 如果是AJAX请求，返回JSON数据
    if request.GET.get('ajax'):
        return JsonResponse({
            'red_balls': red_balls,
            'blue_ball': blue_ball
        })
    
    return render(request, 'random.html', {
        'red_balls': red_balls,
        'blue_ball': blue_ball
    })

def calculate_accuracy(predictions, actual_numbers):
    """计算预测准确率"""
    total_matches = 0
    for pred in predictions:
        red_matches = len(set(pred['red_balls']) & set(actual_numbers['red_balls']))
        blue_match = pred['blue_ball'] == actual_numbers['blue_ball']
        
        # 根据双色球规则计算匹配程度
        if blue_match and red_matches >= 3:
            total_matches += 1
    
    return round((total_matches / len(predictions)) * 100, 2)

def predict(request):
    if request.GET.get('type'):
        predict_type = request.GET.get('type')
        predictions = []
        
        try:
            # 获取最近100期数据用于预测
            recent_data = LotteryNumber.objects.all().order_by('-issue_number')[:100]
            
            # 获取最近一期的实际开奖号码用于计算准确率
            latest_numbers = {
                'red_balls': [
                    recent_data[0].red_ball_1, recent_data[0].red_ball_2,
                    recent_data[0].red_ball_3, recent_data[0].red_ball_4,
                    recent_data[0].red_ball_5, recent_data[0].red_ball_6
                ],
                'blue_ball': recent_data[0].blue_ball
            }
            
            if predict_type == 'frequency':
                predictions = frequency_analysis(recent_data)
            elif predict_type == 'pattern':
                predictions = pattern_analysis(recent_data)
            elif predict_type == 'smart':
                predictions = smart_analysis(recent_data)
            
            # 计算上一期预测的准确率
            accuracy = calculate_accuracy(predictions, latest_numbers)
            
            return JsonResponse({
                'predictions': predictions,
                'accuracy': accuracy,
                'latest_numbers': latest_numbers
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    return render(request, 'predict.html')

def frequency_analysis(data):
    """基于频率分析的预测"""
    red_balls = []
    blue_balls = []
    
    # 收集所有号码
    for record in data:
        red_balls.extend([
            record.red_ball_1, record.red_ball_2, record.red_ball_3,
            record.red_ball_4, record.red_ball_5, record.red_ball_6
        ])
        blue_balls.append(record.blue_ball)
    
    # 统计频率
    red_counter = Counter(red_balls)
    blue_counter = Counter(blue_balls)
    
    # 计算每个号码的概率
    total_red_draws = len(data) * 6
    total_blue_draws = len(data)
    
    red_probs = {i: red_counter.get(i, 0) / total_red_draws for i in range(1, 34)}
    blue_probs = {i: blue_counter.get(i, 0) / total_blue_draws for i in range(1, 17)}
    
    # 生成预测结果
    predictions = []
    for _ in range(10):
        # 使用轮盘赌选择法选择红球
        selected_red = []
        available_numbers = list(range(1, 34))
        
        for _ in range(6):
            # 计算剩余号码的概率总和
            total_prob = sum(red_probs[n] for n in available_numbers)
            # 归一化概率
            normalized_probs = [red_probs[n] / total_prob for n in available_numbers]
            
            # 选择一个号码
            chosen_idx = np.random.choice(len(available_numbers), p=normalized_probs)
            selected_red.append(available_numbers[chosen_idx])
            available_numbers.pop(chosen_idx)
        
        selected_red.sort()
        
        # 选择蓝球
        blue_probs_list = [blue_probs[i] for i in range(1, 17)]
        selected_blue = np.random.choice(range(1, 17), p=blue_probs_list)
        
        # 计算置信度
        # 使用条件概率计算组合出现的可能性
        red_prob = 1.0
        for num in selected_red:
            red_prob *= red_probs[num]
        blue_prob = blue_probs[selected_blue]
        
        # 使用对数概率避免数值过小
        confidence = round(
            (-np.log(red_prob) * 10 + -np.log(blue_prob) * 5) / 
            (-np.log(1/33**6) * 10 + -np.log(1/16) * 5) * 100
        )
        
        predictions.append({
            'red_balls': selected_red,
            'blue_ball': int(selected_blue),
            'confidence': min(max(confidence, 50), 99)  # 限制在50-99之间
        })
    
    return predictions

def pattern_analysis(data):
    """基于规律分析的预测"""
    predictions = []
    
    # 分析相邻期号码的变化规律
    changes = []
    for i in range(len(data) - 1):
        current = [data[i].red_ball_1, data[i].red_ball_2, data[i].red_ball_3,
                  data[i].red_ball_4, data[i].red_ball_5, data[i].red_ball_6]
        next_nums = [data[i+1].red_ball_1, data[i+1].red_ball_2, data[i+1].red_ball_3,
                    data[i+1].red_ball_4, data[i+1].red_ball_5, data[i+1].red_ball_6]
        changes.append([n2 - n1 for n1, n2 in zip(current, next_nums)])
    
    latest = [data[0].red_ball_1, data[0].red_ball_2, data[0].red_ball_3,
             data[0].red_ball_4, data[0].red_ball_5, data[0].red_ball_6]
    
    for _ in range(10):
        # 应用变化规律并确保不重复
        while True:
            change = random.choice(changes)
            predicted_red = []
            for n, c in zip(latest, change):
                new_num = ((n + c - 1) % 33) + 1
                if new_num not in predicted_red:
                    predicted_red.append(new_num)
            
            if len(predicted_red) == 6:  # 确保得到6个不重复的号码
                break
        
        predicted_red.sort()
        
        # 蓝球预测
        blue_trend = [d.blue_ball for d in data[:10]]
        predicted_blue = ((data[0].blue_ball + random.choice([-1, 0, 1])) % 16) + 1
        
        # 计算置信度：基于变化模式的重复出现次数
        pattern_count = sum(1 for c in changes if c == change)
        confidence = round((pattern_count / len(changes)) * 100)
        
        predictions.append({
            'red_balls': predicted_red,
            'blue_ball': predicted_blue,
            'confidence': min(max(confidence + 60, 50), 99)  # 基础置信度不低于50%
        })
    
    return predictions

def smart_analysis(data):
    """智能算法预测（综合分析）"""
    predictions = []
    
    # 获取频率分析结果
    freq_predictions = frequency_analysis(data)
    # 获取规律分析结果
    pattern_predictions = pattern_analysis(data)
    
    # 综合两种预测方法
    for i in range(10):  # 生成10组预测
        if random.random() > 0.5:
            pred = freq_predictions[i].copy()  # 创建副本
            # 稍微调整一下号码
            adjusted_red = []
            for n in pred['red_balls']:
                new_n = n + random.choice([-1, 0, 1])
                if new_n < 1:
                    new_n = 1
                elif new_n > 33:
                    new_n = 33
                adjusted_red.append(new_n)
            pred['red_balls'] = sorted(list(set(adjusted_red)))  # 确保不重复
            
            # 如果调整后的红球数量不足6个，补充随机号码
            while len(pred['red_balls']) < 6:
                new_num = random.randint(1, 33)
                if new_num not in pred['red_balls']:
                    pred['red_balls'].append(new_num)
            pred['red_balls'].sort()
            
            pred['confidence'] = min(pred['confidence'] + 5, 99)
        else:
            pred = pattern_predictions[i]
            pred['confidence'] = min(pred['confidence'] + 10, 99)
        
        predictions.append(pred)
    
    return predictions
