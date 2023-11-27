<?php
//this
$whois_quantity = 50;
set_time_limit($whois_quantity*3);
function getWebsiteInfo($domain, $whoisPath) {
    // 使用 shell_exec 調用指定路徑下的 whois 命令
    $whois_result = shell_exec("$whoisPath\\whois64 -accepteula $domain");
    //$whois_result = shell_exec("$whoisPath\\whois $domain whois.iana.org");

    return $whois_result;
}

function getpart($result, $part) {
    $pattern = "/$part (.+?)\n/";
    preg_match($pattern, $result, $matches);
    if (isset($matches[1])) {
        return $matches[1];
    } else {
        return null;
    }
}

//this
$whoisPath = 'E:\NetworkTool\WhoIs';


$filePath = 'badurl.txt';

// 使用file_get_contents函数读取整个文件的内容
$fileContent = file_get_contents($filePath);

// 使用explode按照'. \n'进行分隔
$lines = explode(".\n", $fileContent);



$host = "localhost";$username = "root";$password = "0615";$database = "Whois_db";
$conn = mysqli_connect($host, $username, $password, $database);
if ($conn === false) {
    echo "Error!!!";
    die(mysqli_connect_error());  // 获取连接错误信息
}




$time=0;
foreach ($lines as $line) {
    $startTime = microtime(true);

    $result = getWebsiteInfo($line, $whoisPath);

    $part = "Updated Date:";
    $date = getpart($result, $part);

    $part = "Creation Date:";
    $date2 = getpart($result, $part);

    $part = "Registrant Country:";
    $Country = getpart($result, $part);

    //if all catch fall,order true whois server
    if($date == null and $date2 == null and $Country == null){
        $Iana_result = shell_exec("$whoisPath\\whois $line whois.iana.org");
        $whois_server = getpart($Iana_result, "whois:");//find ture whois server
        $result = shell_exec("$whoisPath\\whois $line $whois_server");//use whois server
        $part = "Updated Date:";
        $date = getpart($result, $part);

        $part = "Creation Date:";
        $date2 = getpart($result, $part);

        $part = "Registrant Country:";
        $Country = getpart($result, $part);

            if($date == null and $date2 == null and $Country == null){//.sk format
                $part = "Updated:";
                $date = getpart($result, $part);

                $part = "Created:";
                $date2 = getpart($result, $part);

                $part = "Country Code:";
                $Country = getpart($result, $part);
                    if($date == null and $date2 == null and $Country == null){//.tw format
                        $part = "Record created on";
                        $date2 = getpart($result, $part);
        
                        $Address_lines = explode("\n", $Iana_result);
                        foreach ($Address_lines as $Address_line) {
                            if (preg_match('/^\s*address:\s*(.+)$/i', $Address_line, $Addressmatches)) {
                                $Country = trim($Addressmatches[1]);
                            }
                        }
                            
                    }
            }
    }else if($Country == null){
        $Iana_result = shell_exec("$whoisPath\\whois $line whois.iana.org");
        
        $Address_lines = explode("\n", $Iana_result);
        foreach ($Address_lines as $Address_line) {
            if (preg_match('/^\s*address:\s*(.+)$/i', $Address_line, $Addressmatches)) {
                $Country = trim($Addressmatches[1]);
            }
        }
    }
    
    $sql = "INSERT INTO whoisdata (doman_name, update_data, create_data, country) VALUES ('$line', '$date', '$date2', '$Country')";

    if (mysqli_query($conn, $sql)) {
        echo "Doman_name: " . $line . ' ';
        echo '最後跟新時間: ' . $date . ' ';
        echo 'DNS註冊時間: ' . $date2 . ' ';
        echo '所在國家: ' . $Country . '<br>';
    } else {
        echo "Error executing query: " . mysqli_error($conn);
        break;
    }


    $endTime = microtime(true);
    $iterationTime = $endTime - $startTime;

    $time += $iterationTime;

    echo '這次whois詢問花費時間: ' . $iterationTime . ' 秒<br>';

}

echo '總花費時間: ' . ob_get_length() . ' 秒';

mysqli_close($conn);
?>
