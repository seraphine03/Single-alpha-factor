
# coding: utf-8

# In[ ]:

from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import AverageDollarVolume
from quantopian.pipeline.filters.morningstar import Q1500US
from quantopian.pipeline.data.sentdex import sentiment

from quantopian.pipeline.data.morningstar import asset_classification
from quantopian.pipeline.data.morningstar import operation_ratios, valuation_ratios
 
def initialize(context):
    """
    Called once at the start of the algorithm.
    """   
    # Rebalance every day, 1 hour after market open.
    schedule_function(my_rebalance, date_rules.every_day(), time_rules.market_open(hours=1))
     
    # Record tracking variables at the end of each day.
    schedule_function(my_record_vars, date_rules.every_day(), time_rules.market_close())
     
    # Create our dynamic stock selector.
    attach_pipeline(make_pipeline(), 'my_pipeline')
    
    #set_commission(commission.PerTrade(cost=0.001))
         
def make_pipeline():
    testing_factor = asset_classification.financial_health_grade #that's our factor
    universe = (Q1500US() & testing_factor.notnull()) #both companies in q1500us and we have a value for the operation ratio
    testing_factor = testing_factor.rank(mask=universe, method= 'average') #this will rank our revenue growth
    pipe = Pipeline(columns={'testing_factor':testing_factor},
                   screen=universe)
    return pipe

 
def before_trading_start(context, data):
    """
    Called every day before market open.
    """
    context.output = pipeline_output('my_pipeline')
  
    # These are the securities that we are interested in trading each day.
    context.security_list = context.output.index

 
def my_rebalance(context,data):
    """
    Execute orders according to our schedule_function() timing. 
    """
    #strategy and logic of trading.
    long_secs = context.output[context.output['longs']].index
    long_weight = 0.5/len(long_secs) #index is the ticker 
                                               
    short_secs = context.output[context.output['shorts']].index
    short_weight = -0.5/len(short_secs) #index is the ticker
    #half is longing, half is shorting the stocks so beta is close to neutral which is good
    
    #checks
    for security in long_secs:
        if data.can_trade(security):
            order_target_percent(security,long_weight)
    
    for security in short_secs:
        if data.can_trade(security):
            order_target_percent(security,short_weight)
    
    for security in context.portfolio.positions:
        if data.can_trade(security) and security not in long_secs and security not in short_secs:
            order_target_percent(security,0)
 
def my_record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    long_count = 0
    short_count = 0
    for position in context.portfolio.positions.itervalues():
        if position.amount > 0:
            long_count += 1
        elif position.amount < 0:
            short_count += 1
    record(num_longs = long_count, num_short = short_count, leverage=context.account.leverage)

