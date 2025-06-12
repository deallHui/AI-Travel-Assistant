package com.itheima.mybatisplus.service.impl;

import com.itheima.mybatisplus.pojo.User;
import com.itheima.mybatisplus.mapper.UserMapper;
import com.itheima.mybatisplus.service.IUserService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;

/**
 * <p>
 *  服务实现类
 * </p>
 *
 * @author H
 * @since 2025-04-15
 */
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements IUserService {

}
