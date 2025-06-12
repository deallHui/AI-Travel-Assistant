package com.itheima.mybatisplus.controller;

import com.itheima.mybatisplus.pojo.User;
import com.itheima.mybatisplus.service.IUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * <p>
 *  前端控制器
 * </p>
 *
 * @author H
 * @since 2025-04-15
 */
@RestController
@RequestMapping("/user")
public class UserController {

    @Autowired
    private IUserService userService;

    // 插入一条记录（选择字段，策略插入）：boolean save(T entity);
    @PostMapping("/add")
    public void add(String name, Integer age, String email) {
        User user = new User();
        user.setName(name);
        user.setAge(age);
        user.setEmail(email);
        boolean result = userService.save(user);
        if (result) {
            System.out.println("User saved successfully.");
        } else {
            System.out.println("Failed to save user.");
        }
    }

    // 根据 ID 删除：boolean removeById(Serializable id);
    @DeleteMapping("/del")
    public void del(Long id) {
        boolean result = userService.removeById(id);
        if (result) {
            System.out.println("User deleted successfully.");
        } else {
            System.out.println("Failed to delete user.");
        }
    }

    // 根据 ID 选择修改：boolean updateById(T entity);
    @PutMapping("/update")
    public void update(Long id, String email) {
        User updateUser = new User();
        updateUser.setId(id);
        updateUser.setEmail(email);
        boolean result = userService.updateById(updateUser);
        if (result) {
            System.out.println("User updated successfully.");
        } else {
            System.out.println("Failed to update user.");
        }
    }

    // 根据 ID 查询：T getById(Serializable id);
    @GetMapping("/get")
    public User get(Long id) {
        User user = userService.getById(id);
        if (user != null) {
            System.out.println("User found: " + user);
        } else {
            System.out.println("User not found.");
        }
        return user;
    }
}
