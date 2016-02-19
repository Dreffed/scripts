1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
CREATE FUNCTION [dbo].[parseJSON]
(
    @jsonStr VARCHAR(MAX)
)
RETURNS @output TABLE(
      keyName VARCHAR(255)
    , data VARCHAR(255)
)
BEGIN
 
DECLARE
      @braceStartDL CHAR(1)
    , @braceEndDL CHAR(1)
    , @quoteDL CHAR(1)
    , @kvseperatorDL CHAR(1)
    , @seperatorDL CHAR(1)
    , @braceStart INT
    , @braceEnd INT
    , @quote INT
    , @kvseperator INT
    , @seperator INT
    , @kvStart INT
    , @jsonRev VARCHAR(MAX)
    , @kvStr VARCHAR(MAX)
    , @kvName VARCHAR(MAX)
    , @kvValue VARCHAR(MAX)
 
    SELECT
          @braceStartDL = '{'
        , @braceEndDL = '}'
        , @quoteDL = '"'
        , @kvseperatorDL = ':'
        , @seperatorDL = ','
        , @braceStart = CHARINDEX(@braceStartDL, @jsonStr)
        , @jsonRev = REVERSE(@jsonStr)
        , @braceEnd = CHARINDEX(@braceEndDL, @jsonRev)
        , @quote = CHARINDEX(@quoteDL, @jsonStr)
        , @kvseperator = CHARINDEX(@kvseperatorDL, @jsonStr)
        , @seperator = CHARINDEX(@seperatorDL, @jsonStr)
 
    -- Now we have vlaues
    -- first check for a JSON OBject..
    IF @braceStart = 1
    BEGIN
        -- we have a JSON Object...
        -- break it out...
        SELECT @kvStr = SUBSTRING(@jsonStr, @braceStart+1, LEN(@jsonStr) - @braceEnd-1)
        --PRINT 'Recursive call...' + @kvStr
        -- now we pass this down to function again
        INSERT INTO @output
                ( keyName, data )
        SELECT * FROM dbo.parseJSON(@kvStr)
        RETURN
    END
 
    -- we now should have a kv string...
    -- "<fieldName>" : "<fieldvalue>"[, "<fieldName>" : "<fieldvalue>"[, ...]]
    -- we need 3 elements to do this properly...
    -- fist kvpair, delimted by @seperator
    --  name of kv pair delimeted by @kvseperator
    --  value of kvPair string between @seperator and @kvseperator
    SELECT @kvStart = 0
        , @kvseperator = CHARINDEX(@kvseperatorDL, @jsonStr, @kvStart)
        , @seperator = CHARINDEX(@seperatorDL, @jsonStr, @kvseperator)
 
    WHILE @kvStart < LEN(@jsonStr)
    BEGIN
        --SELECT @kvStart, @kvseperator, @seperator
        IF @seperator = 0 
        BEGIN
            SELECT @seperator = LEN(@jsonStr)
        END
 
        -- now to split the fields
        -- the caveat to remember is if the field is a json object, we split and recall...
        SELECT @kvName = SUBSTRING(@jsonStr, @kvStart, @kvseperator-@kvStart)
            , @kvValue = SUBSTRING(@jsonStr, @kvseperator+1, @seperator - @kvseperator-1) 
        --SELECT @kvName, @kvValue
 
        -- now to check for nested objects...
        IF LEFT(@kvValue, 1) = @braceStartDL
        BEGIN
            -- we have a split...
            SELECT @kvValue = SUBSTRING(@jsonStr, @kvseperator+2, LEN(@jsonStr) - @kvseperator-2)
            INSERT INTO @output (keyName, data) 
            VALUES(@kvName, @kvValue);
 
            -- now to parse this substring...
            --PRINT 'Recursive call...' + @kvValue
            INSERT INTO @output
                    ( keyName, data )
            SELECT * FROM dbo.parseJSON(@kvValue)
            BREAK
        END
        ELSE
        BEGIN
            INSERT INTO @output (keyName, data) 
            VALUES(@kvName, @kvValue);
        END
        -- now to set for the next field...
        SELECT @kvStart = @seperator + 1
            , @kvseperator = CHARINDEX(@kvseperatorDL, @jsonStr, @kvStart)
            , @seperator = CHARINDEX(@seperatorDL, @jsonStr, @kvseperator)
    END
    RETURN
END
GO
 
/* -- test scripts
DECLARE @jsonStr AS VARCHAR(MAX)
SELECT @jsonStr = '{"vfdata":{"COUNTRY_CODE":"CA", "NAME":"product_name", "CREATIVE_CODE":"default", "LOGO_PIXEL_SIZE":"http://getourlogo.com/adacado_logo.png", "TEXT_MENTION":"Data driven dynamic-creative", "URL":"http://www.adacado.com"}}'
SELECT * FROM dbo.parseJSON(@jsonStr)
SELECT @jsonStr = '"vfdata":{"COUNTRY_CODE":"CA", "NAME":"product_name", "CREATIVE_CODE":"default", "LOGO_PIXEL_SIZE":"http://getourlogo.com/adacado_logo.png", "TEXT_MENTION":"Data driven dynamic-creative", "URL":"http://www.adacado.com"}'
SELECT * FROM dbo.parseJSON(@jsonStr)
SELECT @jsonStr = '"COUNTRY_CODE":"CA", "NAME":"product_name", "CREATIVE_CODE":"default", "LOGO_PIXEL_SIZE":"http://getourlogo.com/adacado_logo.png", "TEXT_MENTION":"Data driven dynamic-creative", "URL":"http://www.adacado.com"'
SELECT * FROM dbo.parseJSON(@jsonStr)
-- */