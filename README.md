

# Class Diagram
```mermaid
classDiagram
    class User {
        - name: String
        - createDate: Date
        - birthday: Date
        - gender: String
        - grade: String
        - recentView: List<Item>
        - pointBalance: Double
        + login()
        + logout()
        + register()
        + withdraw()
    }
    
    class MyPage {
        - orderHistory: List<Order>
        - userComments: List<Comment>
        - inquiries: List<Inquiry>
        - notifications: List<String>
        + viewOrderHistory()
        + viewUserInfo()
        + viewComments()
        + viewInquiries()
    }
    
    class Cart {
        - items: List<Item>
        - totalPrice: Double
        - status: String
        + addItem()
        + removeItem()
        + updateQuantity()
    }
    
    class Order {
        - orderList: List<Item>
        - total: Double
        - deliveryFee: Double
        - deliveryStatus: String
        - requestMessage: String
        + placeOrder()
        + cancelOrder()
    }
    
    class Store {
        - name: String
        - address: String
        - phoneNumber: String
        - likes: Integer
        - mapApi: Map
        + viewMenu()
        + getStoreInfo()
    }
    
    class Item {
        - name: String
        - price: Double
        - description: String
    }
    
    class Comment {
        - rating: Integer
        - text: String
        - author: User
        + createComment()
        + deleteComment()
    }
    
    class Address {
        - street: String
        - city: String
        - zipCode: String
        - isPrimary: Boolean
    }
    
    class PaymentMethod {
        - type: String
        - maskedInfo: String
    }
    
    class Coupon {
        - name: String
        - discountValue: Double
        - expirationDate: Date
        - isUsed: Boolean
    }

    User "1" -- "1" MyPage
    User "1" -- "1..*" Order
    User "1" -- "1" Cart
    User "1" -- "0..*" Address
    User "1" -- "0..*" PaymentMethod
    User "1" -- "0..*" Coupon

    Cart "1" -- "*" Item
    Order "1" -- "*" Item
    Order "1" -- "1" Address
    Order "1" -- "1" PaymentMethod
    Order "1" -- "0..1" Coupon

    Store "1" -- "*" Item
    Store "1" -- "*" Comment
    User "1" -- "*" Comment
```

# 결제 순서도
```mermaid
flowchart TD
    A[사용자] --> B{메뉴 선택 및 장바구니 추가};
    B --> C{장바구니 확인};
    C --수정--> B;
    C --주문--> D[주문 페이지];
    D --> E{주문 정보 입력};
    E --주소/요청 사항--> F{쿠폰/포인트 적용};
    F --> G{최종 금액 확인};
    G --결제--> H[결제 수단 선택];
    H --> I{결제 정보 입력};
    I --> J[결제 진행];
    J --결제 실패--> H;
    J --결제 성공--> K[주문 완료];
    K --> L[주문 내역 확인];
```
순서도 설명:

- 시작: 사용자가 메뉴를 선택합니다.

- 의사 결정: 장바구니에서 메뉴를 수정할지, 바로 주문할지 결정합니다.

- 주문 페이지: 배달 정보와 할인 정보를 입력하는 단계입니다.

- 결제: 결제 수단과 정보를 입력하고 결제를 시도합니다.
 
- 분기점: 결제 성공 여부에 따라 다음 단계가 나뉩니다.
 
- 종료: 결제가 완료되면 주문 내역을 확인할 수 있습니다.

# 결제 시퀀스 다이어그램
```mermaid
sequenceDiagram
    participant User
    participant FrontEnd
    participant BackEnd
    participant PaymentGateway
    participant Database

    User->>FrontEnd: 메뉴 선택 및 장바구니 추가
    FrontEnd->>BackEnd: /cart/add 요청
    BackEnd->>Database: 장바구니 정보 저장
    Database-->>BackEnd: 성공 응답
    BackEnd-->>FrontEnd: 장바구니 업데이트
    
    User->>FrontEnd: '주문하기' 버튼 클릭
    FrontEnd->>BackEnd: /order/create 요청
    BackEnd->>BackEnd: 최종 금액 계산(쿠폰, 배달비)
    BackEnd->>FrontEnd: 주문 정보 응답
    
    User->>FrontEnd: 결제 수단 선택 및 '결제' 버튼 클릭
    FrontEnd->>PaymentGateway: 결제 요청(결제 정보, 금액)
    PaymentGateway-->>FrontEnd: 결제 결과 응답
    
    alt 결제 성공
        FrontEnd->>BackEnd: /order/complete 요청
        BackEnd->>Database: 주문 상태 업데이트
        Database-->>BackEnd: 성공 응답
        BackEnd-->>FrontEnd: 주문 완료 응답
        FrontEnd->>User: '주문이 완료되었습니다' 메시지 표시
    else 결제 실패
        FrontEnd->>User: '결제 실패' 메시지 표시
    end
```
시퀀스 다이어그램 설명:

- 메뉴 선택: 사용자가 메뉴를 선택하면 프론트엔드가 백엔드에 장바구니 추가 요청을 보냅니다.
 
- 주문 생성: 주문하기 버튼을 누르면 백엔드에서 최종 금액을 계산하고 주문 정보를 준비합니다.
 
- 결제 요청: 프론트엔드가 결제 게이트웨이에 직접 결제를 요청하고, 그 결과를 받습니다.
 
- 결과 반영: 결제 성공 시, 백엔드에 최종 주문 완료를 알리고 데이터베이스에 상태를 업데이트합니다. 결제 실패 시, 사용자에게 실패 메시지를 바로 보여줍니다.