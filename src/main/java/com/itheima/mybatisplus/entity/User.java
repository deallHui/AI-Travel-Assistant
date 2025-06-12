package com.itheima.mybatisplus.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("user")
public class User {
    private Long id;
    private String name;
    private int age;
    private String email;
}
