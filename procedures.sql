DROP PROCEDURE IF EXISTS RegisterUser;
DROP PROCEDURE IF EXISTS LoginUser;
DROP PROCEDURE IF EXISTS AddRecipe;
DROP PROCEDURE IF EXISTS GetRecipesLike;
DROP PROCEDURE IF EXISTS GetRecipeById;
DROP PROCEDURE IF EXISTS GetIngrMeasurFromRecipe;
DROP PROCEDURE IF EXISTS GetAllUserRestrictions;
DROP PROCEDURE IF EXISTS ShowAvoidedIngredients;
DROP PROCEDURE IF EXISTS GetUnderSpecficCalorieCount;
DROP PROCEDURE IF EXISTS GetMealPlanIngredients;
DROP PROCEDURE IF EXISTS GetWeekRecipesByType;
DROP PROCEDURE IF EXISTS GetMealPlanForWeek;
DROP PROCEDURE IF EXISTS GetMealPlanUnderSpecifiedCalorieCount;
DROP TRIGGER IF kitchen_trigger;
DROP PROCEDURE IF EXISTS recipeinstruction;


/* Procedures */

DELIMITER //
CREATE PROCEDURE RegisterUser(IN firstname VARCHAR(255),IN lastname VARCHAR(255),IN address VARCHAR(255),IN email VARCHAR(255),IN password VARCHAR(255),IN phonenumber VARCHAR(30),IN image VARCHAR(255),IN dob DATE)
BEGIN INSERT INTO user(user_firstname,user_lastname,user_address,user_email,user_password,user_phonenumber,user_image,user_dob) VALUES(firstname,lastname,address,email,password,phonenumber,image,dob);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE LoginUser(IN email VARCHAR(255),IN password VARCHAR(255))
BEGIN (SELECT user.user_email from user WHERE user.user_email=email AND user.user_password=password
);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE AddRecipe(IN name VARCHAR(120),IN recipetype VARCHAR(30),IN image VARCHAR(255),IN serving DECIMAL(11,2),IN preptime INT(11),IN creationdate DATE,IN caloriecount INT(11))
BEGIN INSERT INTO recipe(recipe_name,recipe_type, recipe_image, recipe_serving, recipe_preptime,recipe_creationdate,recipe_caloriecount) VALUES(name,recipetype,image,serving,preptime,creationdate,caloriecount);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetRecipesLike(IN name VARCHAR(120))
BEGIN (
    SELECT * from recipe WHERE recipe.recipe_name LIKE name
    ORDER BY recipe.recipe_creationdate DESC
);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetRecipeById(IN id INT)
BEGIN (
SELECT * FROM recipe WHERE recipe.recipe_id=id
);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetIngrMeasurFromRecipe(IN id INT)
BEGIN (
SELECT measurement.measurement_name, ingredient.ingredient_name, use_ingredients.ingredient_quantity FROM measurement
JOIN ingredient JOIN use_ingredients ON
use_ingredients.recipe_id IN
(SELECT use_ingredients.recipe_id FROM use_ingredients WHERE use_ingredients.recipe_id=id)
AND measurement.measurement_id=use_ingredients.measurement_id
AND ingredient.ingredient_id=use_ingredients.ingredient_id
);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetAllUserRestrictions(IN firstname VARCHAR(255), IN lastname VARCHAR(255))
BEGIN (SELECT userrestriction.restriction_name
FROM user JOIN user_has_restriction JOIN userrestriction
ON user.user_id=user_has_restriction.user_id AND user_has_restriction.restriction_id=userrestriction.restriction_id
WHERE user.user_firstname=firstname AND user.user_lastname=lastname);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE ShowAvoidedIngredients(IN restriction VARCHAR(50))
BEGIN (SELECT ingredient.ingredient_name
FROM userrestriction JOIN limits JOIN ingredient
ON userrestriction.restriction_id=limits.restriction_id AND limits.ingredient_id=ingredient.ingredient_id
WHERE userrestriction.restriction_name = restriction);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetUnderSpecficCalorieCount(IN caloriecount INT(11))
BEGIN (SELECT *
FROM recipe
WHERE recipe.recipe_caloriecount <= caloriecount);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetMealPlanIngredients(IN mlplnid INT)
BEGIN (SELECT use_ingredients.ingredient_id
    FROM use_ingredients
    WHERE use_ingredients.recipe_id IN
    (
        SELECT  use_recipe.recipe_id
        FROM (
            SELECT * FROM plan_meal_day
            WHERE mealplan_id = mlplnid) AS mealplanrec
        JOIN use_recipe
        ON mealplanrec.recipe_id = use_recipe.recipe_id
    ) GROUP BY use_ingredients.ingredient_id
);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetWeekRecipesByType(IN mltyp VARCHAR(50))
BEGIN (SELECT recipe.recipe_name, recipe.recipe_id FROM recipe WHERE recipe.recipe_type = mltyp
ORDER BY RAND()
LIMIT 7);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetMealPlanForWeek(IN mlplnid INT)
BEGIN (SELECT mealplanday.mealplanday_id, mealplanday.day, mealplanday.mealtype
  FROM mealplanday
  WHERE mealplanday.mealplanday_id IN
  (
      SELECT plan_meal_day.mealplanday_id
      FROM plan_meal_day
  WHERE mealplan_id = mlplnid)
  )
);
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE GetMealPlanUnderSpecifiedCalorieCount(IN mlplnid INT, IN caloriecount INT)
BEGIN (SELECT *
  FROM mealplanday
  WHERE mealplanday.mealplanday_id IN
  (
      SELECT plan_meal_day.mealplanday_id
      FROM plan_meal_day
  WHERE mealplan_id = mlplnid)
  AND mealplanday.caloriecount<=caloriecount
  )
);
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER kitchen_trigger
AFTER insert ON user
FOR EACH ROW
BEGIN
INSERT into kitchen values (0)
INSERT into user_kitchen(kitchen_id) values(
(SELECT LAST_INSERT_ID() FROM user LIMIT 1
)
(SELECT LAST_INSERT_ID() FROM kitchen LIMIT 1
)
);

END //
DELIMITER;

DELIMITER //
CREATE PROCEDURE recipeinstruction (IN recp_id INT )
BEGIN (
SELECT instruction.instruction_details, follow_instruction.instruction_order
FROM follow_instruction JOIN instruction
ON follow_instruction.instruction_id = instruction.instruction_id
WHERE follow_instruction.recipe_id = recp_id
ORDER BY follow_instruction.instruction_order);
END //
DELIMITER ;
