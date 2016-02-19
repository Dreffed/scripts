
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
