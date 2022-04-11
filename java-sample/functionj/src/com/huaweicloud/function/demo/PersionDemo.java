package com.huaweicloud.function.demo;

import com.huaweicloud.function.demo.entity.*;
import com.huawei.services.runtime.Context;
import com.huawei.services.runtime.RuntimeLogger;

public class PersionDemo {
	public void persionTrigger(Person p, Context context) {
		RuntimeLogger logger = context.getLogger();
		logger.log(p.getName() + " is " + p.getAge());
	}

	
}
