mybatis-mapper2sql
==================
[![Build Status](https://travis-ci.org/hhyo/mybatis-mapper2sql.svg?branch=master)](https://travis-ci.org/hhyo/mybatis-mapper2sql)
[![codecov](https://codecov.io/gh/hhyo/mybatis-mapper2sql/branch/master/graph/badge.svg)](https://codecov.io/gh/hhyo/mybatis-mapper2sql)
[![image](https://img.shields.io/pypi/v/mybatis-mapper2sql.svg)](https://pypi.org/project/mybatis-mapper2sql/)
[![image](https://img.shields.io/pypi/l/mybatis-mapper2sql.svg)](https://github.com/hhyo/mybatis-mapper2sql/blob/master/LICENSE)
[![image](https://img.shields.io/pypi/pyversions/mybatis-mapper2sql.svg)](https://pypi.org/project/mybatis-mapper2sql/)

Generate SQL Statements from the MyBatis3 Mapper XML file   
**Just for SQL Review https://github.com/hhyo/archery/issues/3**

Installation
------------
`pip install mybatis-mapper2sql`


Usage
-------------

```python
import mybatis_mapper2sql
# Parse Mybatis Mapper XML files
mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(xml='mybatis_mapper.xml')
# Get All SQL Statements from Mapper
statement = mybatis_mapper2sql.get_statement(mapper)
# Get SQL Statement By SQLId
statement = mybatis_mapper2sql.get_child_statement(mapper, sql_id)
```

Examples
-------------
> https://github.com/OldBlackJoe/mybatis-mapper

#### test.xml ####
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="Test">
    <sql id="sometable">
        fruits
    </sql>
    <sql id="somewhere">
        WHERE
        category = #{category}
    </sql>
    <sql id="someinclude">
        FROM
        <include refid="${include_target}"/>
        <include refid="somewhere"/>
    </sql>
    <select id="testParameters">
        SELECT
        name,
        category,
        price
        FROM
        fruits
        WHERE
        category = #{category}
        AND price > ${price}
    </select>
    <select id="testInclude">
        SELECT
        name,
        category,
        price
        <include refid="someinclude">
            <property name="prefix" value="Some"/>
            <property name="include_target" value="sometable"/>
        </include>
    </select>
    <select id="testIf">
        SELECT
        name,
        category,
        price
        FROM
        fruits
        WHERE
        1=1
        <if test="category != null and category !=''">
            AND category = #{category}
        </if>
        <if test="price != null and price !=''">
            AND price = ${price}
            <if test="price >= 400">
                AND name = 'Fuji'
            </if>
        </if>
    </select>
    <select id="testTrim">
        SELECT
        name,
        category,
        price
        FROM
        fruits
        <trim prefix="WHERE" prefixOverrides="AND|OR">
            OR category = 'apple'
            OR price = 200
        </trim>
    </select>
    <select id="testWhere">
        SELECT
        name,
        category,
        price
        FROM
        fruits
        <where>
            AND category = 'apple'
            <if test="price != null and price !=''">
                AND price = ${price}
            </if>
        </where>
    </select>
    <update id="testSet">
        UPDATE
        fruits
        <set>
            <if test="category != null and category !=''">
                category = #{category},
            </if>
            <if test="price != null and price !=''">
                price = ${price},
            </if>
        </set>
        WHERE
        name = #{name}
    </update>
    <select id="testChoose">
        SELECT
        name,
        category,
        price
        FROM
        fruits
        <where>
            <choose>
                <when test="name != null">
                    AND name = #{name}
                </when>
                <when test="category == 'banana'">
                    AND category = #{category}
                    <if test="price != null and price !=''">
                        AND price = ${price}
                    </if>
                </when>
                <otherwise>
                    AND category = 'apple'
                </otherwise>
            </choose>
        </where>
    </select>
    <select id="testForeach">
        SELECT
        name,
        category,
        price
        FROM
        fruits
        <where>
            category = 'apple' AND
            <foreach collection="apples" item="name" open="(" close=")" separator="OR">
                <if test="name == 'Jonathan' or name == 'Fuji'">
                    name = #{name}
                </if>
            </foreach>
        </where>
    </select>
    <insert id="testInsertMulti">
        INSERT INTO
        fruits
        (
        name,
        category,
        price
        )
        VALUES
        <foreach collection="fruits" item="fruit" separator=",">
            (
            #{fruit.name},
            #{fruit.category},
            ${fruit.price}
            )
        </foreach>
    </insert>
    <select id="testBind">
        <bind name="likeName" value="'%' + name + '%'"/>
        SELECT
        name,
        category,
        price
        FROM
        fruits
        WHERE
        name like #{likeName}
    </select>
</mapper>
```
#### test.py ####
Get All SQL Statements from Mapper

```python
import mybatis_mapper2sql
mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(xml='test.xml')
statement = mybatis_mapper2sql.get_statement(mapper, result_type='raw', reindent=True, strip_comments=True)
print(statement)
```

```SQL
SELECT name,
       category,
       price
FROM fruits
WHERE category = ?
  AND price > ?;


SELECT name,
       category,
       price
FROM fruits
WHERE category = ?;


SELECT name,
       category,
       price
FROM fruits
WHERE 1=1
  AND category = ?
  AND price = ?
  AND name = 'Fuji';


SELECT name,
       category,
       price
FROM fruits
WHERE category = 'apple'
  OR price = 200;


SELECT name,
       category,
       price
FROM fruits
WHERE category = 'apple'
  AND price = ?;


UPDATE fruits
SET category = ?,
    price = ?
WHERE name = ?;


SELECT name,
       category,
       price
FROM fruits
WHERE name = ?
  AND category = ?
  AND price = ?
  AND category = 'apple';


SELECT name,
       category,
       price
FROM fruits
WHERE categy = 'apple'
  AND (name = ?
       OR name = ?);


INSERT INTO fruits (name, category, price)
VALUES (?,
        ?,
        ?) , (?,
              ?,
              ?);


SELECT name,
       category,
       price
FROM fruits
WHERE name like ?;
```
Get SQL Statement By SQLId

```python
import mybatis_mapper2sql
mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(xml='test.xml')
statement = mybatis_mapper2sql.get_child_statement(mapper,'testForeach', reindent=True, strip_comments=False)
print(statement)
```


```SQL
SELECT name,
       category,
       price
FROM fruits
WHERE categy = 'apple'
  AND ( name = ? -- if(name == 'Jonathan' or name == 'Fuji')
OR name = ? -- if(name == 'Jonathan' or name == 'Fuji')
)
```

Running the tests
-----------------
`python setup.py test`

Known Limitations
-----------------
- Doesn't support custom parameters
- All sql parameters will be replace  to '?'
- All of the conditionals to apply in \<if\> \<choose\> \<when\> \<otherwise\> element  

Acknowledgments
-----------------
This project was inspired by the following projects and websites:
- https://github.com/OldBlackJoe/mybatis-mapper 
- http://www.mybatis.org/mybatis-3/dynamic-sql.html
- http://www.enmoedu.com/article-205.html
