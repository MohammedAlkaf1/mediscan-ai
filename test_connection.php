<?php
// Test PostgreSQL connection
require_once 'config.php';

echo "<h2>Testing PostgreSQL Connection</h2>";

// Test using pg_connect
echo "<h3>Method 1: pg_connect</h3>";
try {
    $conn = getDBConnection();
    if ($conn) {
        echo "✓ Successfully connected to PostgreSQL database!<br>";
        
        // Test query
        $result = pg_query($conn, "SELECT version()");
        if ($result) {
            $row = pg_fetch_assoc($result);
            echo "PostgreSQL Version: " . $row['version'] . "<br>";
        }
        
        pg_close($conn);
    }
} catch (Exception $e) {
    echo "✗ Connection failed: " . $e->getMessage() . "<br>";
}

echo "<hr>";

// Test using PDO
echo "<h3>Method 2: PDO</h3>";
try {
    $pdo = getPDOConnection();
    echo "✓ Successfully connected using PDO!<br>";
    
    // Test query
    $stmt = $pdo->query("SELECT version()");
    $row = $stmt->fetch();
    echo "PostgreSQL Version: " . $row['version'] . "<br>";
    
    // Check if tables exist
    echo "<h4>Checking tables:</h4>";
    $tables = ['reports', 'report_files', 'extracted_text', 'lab_results', 'explanations'];
    
    foreach ($tables as $table) {
        $stmt = $pdo->query("SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = '$table'
        )");
        $exists = $stmt->fetchColumn();
        
        if ($exists === 't' || $exists === true) {
            echo "✓ Table '$table' exists<br>";
        } else {
            echo "✗ Table '$table' does not exist<br>";
        }
    }
    
} catch (PDOException $e) {
    echo "✗ PDO Connection failed: " . $e->getMessage() . "<br>";
}
?>
