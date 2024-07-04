import time  

def timing_decorator(func):  
    def wrapper(*args, **kwargs):  
        start_time = time.time()  
        result = func(*args, **kwargs)  
        end_time = time.time()  
        execution_time = end_time - start_time  
        print(f"方法 {func.__name__} 的执行时间: {execution_time:.6f} 秒")  
        return result  
    return wrapper

def timing_decorator_async(func):  
    async def wrapper(*args, **kwargs):  
        start_time = time.time()  
        result = await func(*args, **kwargs)  
        end_time = time.time()  
        execution_time = end_time - start_time  
        print(f"异步方法 {func.__name__} 的执行时间: {execution_time:.6f} 秒")  
        return result  
    return wrapper
